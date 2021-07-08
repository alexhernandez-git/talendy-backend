"""Users views."""
# Django
from api.portals.models.portal_members import PortalMember
from api.portals.models.portals import Portal
from api.users.serializers.users import ConfirmUserSerializer, CreateDonationSerializer
from operator import sub
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from stripe.api_resources import plan
from api.users.permissions import IsAccountOwner

# Models
from api.users.models import User, UserLoginActivity, Earning, Follow
from djmoney.money import Money

# Serializers
from api.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignUpSerializer,
    AccountVerificationSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    ValidateChangeEmail,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    IsEmailAvailableSerializer,
    IsUsernameAvailableSerializer,
    InviteUserSerializer,
    GetCurrencySerializer,
    AttachPaymentMethodSerializer,
    DetachPaymentMethodSerializer,
    GetUserByJwtSerializer,
    PaypalConnectSerializer,
    DetailedUserModelSerializer,
    UpdateGeolocation
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Celery
from api.taskapp.tasks import send_confirmation_email, send_feedback_email

import os
import stripe
import json

# Utils
from api.utils import helpers
from api.utils.mixins import AddPortalMixin
from api.utils.paginations import ShortResultsSetPagination

from datetime import timedelta
from django.utils import timezone
import environ
import tldextract
env = environ.Env()


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  AddPortalMixin):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = User.objects.filter(account_deactivated=False, is_staff=False)
    serializer_class = UserModelSerializer
    lookup_field = 'id'
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('first_name', 'last_name', 'username')

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in [
            'signup',
            'login',
            'verify',
            'stripe_webhooks',
            'stripe_webhooks_invoice_payment_failed',
            'forget_password',
            'list_users_with_most_karma',
            'retrieve',
            'list',
                'leave_feedback']:
            permissions = [AllowAny]
        elif self.action in ['update', 'delete', 'partial_update', 'change_password', 'change_email', 'stripe_connect', 'paypal_connect', 'destroy', 'confirm_user', 'update_geolocation']:
            permissions = [IsAccountOwner, IsAuthenticated]
        elif self.action in ['list_users_not_followed']:
            permissions = [IsAuthenticated]
        else:
            permissions = []

        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['partial_update', 'get_user', 'login', 'register']:
            return DetailedUserModelSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'invite_user':
            return InviteUserSerializer
        elif self.action == 'get_currency':
            return GetCurrencySerializer
        return UserModelSerializer

    def get_queryset(self):
        subdomain = tldextract.extract(self.request.META['HTTP_ORIGIN']).subdomain
        portal = None

        try:
            portal = Portal.objects.get(url=subdomain)
        except Portal.DoesNotExist:
            pass

        if portal:
            user = self.request.user
            members = PortalMember.objects.filter(portal=portal).values_list('user__pk')
            members_list = [x[0] for x in members]
            members_list.append(user.pk)

        if self.action == 'list_users_with_most_karma':

            if portal:
                return User.objects.filter(pk__in=members_list, account_deactivated=False, is_staff=False)
            return User.objects.filter(account_deactivated=False, is_staff=False)

        elif self.action == "list_users_not_followed":
            user = self.request.user
            users = Follow.objects.filter(from_user=user).values_list('follow_user__pk')
            users_list = [x[0] for x in users]
            users_list.append(user.pk)

            if portal:
                return User.objects.filter(
                    pk__in=members_list, account_deactivated=False, is_staff=False).exclude(
                    pk__in=users_list)
            return User.objects.filter(
                account_deactivated=False, is_staff=False).exclude(
                pk__in=users_list)

        if portal:
            return User.objects.filter(pk__in=members_list, account_deactivated=False, is_staff=False)
        return User.objects.filter(account_deactivated=False, is_staff=False)

    # User destroy

    def perform_destroy(self, instance):
        instance.email_notifications_allowed = False
        instance.account_deactivated = True
        instance.save()

    @action(detail=True, methods=['patch'])
    def update_geolocation(self, request, *args, **kwargs):
        user = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdateGeolocation(
            user,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = DetailedUserModelSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def leave_feedback(self, request, *args, **kwargs):
        """Check if email passed is correct."""

        send_feedback_email(request.data)
        return Response(status=status.HTTP_200_OK)

    @ action(detail=True, methods=['patch'])
    def make_donation(self, request, *args, **kwargs):
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'

        user = self.get_object()

        partial = request.method == 'PATCH'
        serializer = CreateDonationSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        to_user, user = serializer.save()
        data = {
            "to_user": UserModelSerializer(to_user).data
        }
        if user:
            data['user'] = DetailedUserModelSerializer(user).data
            data['user']['payment_methods'] = helpers.get_payment_methods(stripe, user.stripe_customer_id)
        return Response(data, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['get'])
    def list_users_with_most_karma(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        self.pagination_class = ShortResultsSetPagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @ action(detail=False, methods=['get'])
    def get_currency(self, request, *args, **kwargs):
        """Check if email passed is correct."""
        serializer = self.get_serializer(data=self.request.data)

        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return Response(data=data, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def confirm_user(self, request, *args, **kwargs):
        """Check if email passed is correct."""
        serializer = ConfirmUserSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def is_email_available(self, request, *args, **kwargs):
        """Check if email passed is correct."""
        serializer = IsEmailAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        email = serializer.data
        return Response(data=email, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def is_username_available(self, request, *args, **kwargs):
        """Check if email passed is correct."""
        serializer = IsUsernameAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        return Response(data={"message": "This username is available"}, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def signup(self, request, *args, **kwargs):
        """User sign up."""
        request.data['username'] = helpers.get_random_username()
        invitation_token = None
        if 'invitation_token' in request.data:
            invitation_token = request.data['invitation_token']
        serializer = UserSignUpSerializer(
            data=request.data,
            context={'request': request, 'seller': False, 'invitation_token': invitation_token, "portal": self.portal})
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        user_serialized = UserModelSerializer(user).data
        data = {
            "user": user_serialized,
            "access_token": token
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @ action(detail=False, methods=['get'])
    def send_verification_email(self, request, *args, **kwargs):
        """Send the email confirmation."""
        if request.user.id:
            user = request.user
            send_confirmation_email(user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @ action(detail=False, methods=['post'])
    def login(self, request, *args, **kwargs):
        """User login."""

        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request, 'portal': self.portal}

        )

        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        data = {
            'user': DetailedUserModelSerializer(user, context={"request": request}, many=False).data,
            'access_token': token,
        }

        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'

        stripe_customer_id = data['user']['stripe_customer_id']

        # Buyer payment methods
        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_201_CREATED)

    @ action(detail=False, methods=['post'])
    def change_password(self, request, *args, **kwargs):
        """User login."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def change_email(self, request, *args, **kwargs):
        """Account verification."""
        serializer = ChangeEmailSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def validate_change_email(self, request, *args, **kwargs):
        """Account verification."""
        serializer = ValidateChangeEmail(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        email = serializer.save()
        data = {'message': 'Email changed!', 'email': email}
        return Response(data, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def forget_password(self, request, *args, **kwargs):
        """User login."""
        serializer = ForgetPasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def reset_password(self, request, *args, **kwargs):
        """Account verification."""
        serializer = ResetPasswordSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @ action(detail=False, methods=['post'])
    def verify(self, request, *args, **kwargs):
        """Account verification."""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Verified account!'}
        return Response(data, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['patch'])
    def remove_card(self, request, *args, **kwargs):
        """Remove payment method"""
        user = request.user
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'

        remove = stripe.PaymentMethod.detach(
            request.data.get('payment_method').get('id'),
        )
        return HttpResponse(status=200)

    @ action(detail=False, methods=['post'])
    def paypal_connect(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""
        user = request.user

        partial = request.method == 'PATCH'
        serializer = PaypalConnectSerializer(
            user,
            data=request.data,
            context={"request": request},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['get'])
    def get_user(self, request, *args, **kwargs):
        if request.user.id == None:
            return Response(status=404)
        subdomain = tldextract.extract(request.META['HTTP_ORIGIN']).subdomain
        portal = None

        try:
            portal = Portal.objects.get(url=subdomain)
        except Portal.DoesNotExist:
            pass

        if portal and not PortalMember.objects.filter(user=request.user, portal=portal).exists():
            return Response(status=404)
        data = {
            'user': DetailedUserModelSerializer(request.user, context={"request": request}, many=False).data,

        }
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'

        stripe_customer_id = data['user']['stripe_customer_id']

        # Buyer payment methods
        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data)

    @ action(detail=False, methods=['post'])
    def get_user_by_email_jwt(self, request, *args, **kwargs):
        serializer = GetUserByJwtSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'

        stripe_customer_id = data['user']['stripe_customer_id']

        # Buyer payment methods
        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data)

    @ action(detail=False, methods=['post'])
    def invite_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @ action(detail=False, methods=['get'])
    def list_follows_available(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @ action(detail=False, methods=['patch'])
    def attach_payment_method(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'
        partial = request.method == 'PATCH'
        serializer = AttachPaymentMethodSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = DetailedUserModelSerializer(user, many=False).data

        stripe_customer_id = data['stripe_customer_id']

        # Buyer payment methods
        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)

    @ action(detail=False, methods=['patch'])
    def detach_payment_method(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'
        partial = request.method == 'PATCH'
        serializer = DetachPaymentMethodSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data

        stripe_customer_id = data['stripe_customer_id']

        # Buyer payment methods
        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)
