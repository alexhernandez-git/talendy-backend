"""Users views."""
# Django
from api.users.serializers.users import BecomeASellerSerializer
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
from api.users.models import User, UserLoginActivity, PlanSubscription, plan_subscriptions
import stripe
import json
import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from api.users.permissions import IsAccountOwner

# Models
from api.users.models import Contact
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
    StripeConnectSerializer,
    StripeSellerSubscriptionSerializer,
    GetCurrencySerializer,
    SellerChangePaymentMethodSerializer,
    SellerCancelSubscriptionSerializer,
    SellerReactivateSubscriptionSerializer,
    AttachPaymentMethodSerializer,
    DetachPaymentMethodSerializer,
    GetUserByJwtSerializer
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Celery
from api.taskapp.tasks import send_confirmation_email

import os
from api.utils import helpers


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    lookup_field = 'id'
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('first_name', 'last_name', 'username')

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['signup', 'login', 'verify', 'list', 'retrieve', 'stripe_webhooks', 'forget_password']:
            permissions = [AllowAny]
        elif self.action in ['update', 'delete', 'partial_update', 'change_password', 'change_email', 'stripe_connect']:
            permissions = [IsAccountOwner, IsAuthenticated]

        else:
            permissions = []
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['list', 'partial_update', 'retrieve']:
            return UserModelSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'invite_user':
            return InviteUserSerializer
        elif self.action == 'get_currency':
            return GetCurrencySerializer
        return UserModelSerializer

    def get_queryset(self):
        if self.action == "list_contacts_available":
            user = self.request.user
            users = Contact.objects.filter(from_user=user).values_list('contact_user__pk')
            users_list = [x[0] for x in users]
            users_list.append(user.pk)
            return User.objects.all().exclude(pk__in=users_list)
        return User.objects.all()

    @action(detail=False, methods=['get'])
    def get_currency(self, request):
        """Check if email passed is correct."""
        serializer = self.get_serializer(data=self.request.data)

        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def is_email_available(self, request):
        """Check if email passed is correct."""
        serializer = IsEmailAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        email = serializer.data
        return Response(data=email, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def is_username_available(self, request):
        """Check if email passed is correct."""
        serializer = IsUsernameAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        return Response(data={"message": "This username is available"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def signup_seller(self, request):
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        """User sign up."""
        invitation_token = None
        if 'invitation_token' in request.data:
            invitation_token = request.data['invitation_token']
        serializer = UserSignUpSerializer(
            data=request.data,
            context={'request': request, 'seller': True, 'invitation_token': invitation_token, 'stripe': stripe})
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        user_serialized = UserModelSerializer(user).data
        data = {
            "user": user_serialized,
            "access_token": token
        }

        stripe_customer_id = data['user']['stripe_customer_id']
        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup_buyer(self, request):
        """User sign up."""

        invitation_token = None
        if 'invitation_token' in request.data:
            invitation_token = request.data['invitation_token']
        serializer = UserSignUpSerializer(
            data=request.data,
            context={'request': request, 'seller': False, 'invitation_token': invitation_token})
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        user_serialized = UserModelSerializer(user).data
        data = {
            "user": user_serialized,
            "access_token": token
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def send_verification_email(self, request):
        """Send the email confirmation."""
        if request.user.id:
            user = request.user
            send_confirmation_email(user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""

        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}

        )

        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token,
        }
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'

        stripe_customer_id = data['user']['stripe_customer_id']

        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """User login."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def change_email(self, request):
        """Account verification."""
        serializer = ChangeEmailSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def validate_change_email(self, request):
        """Account verification."""
        serializer = ValidateChangeEmail(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        email = serializer.save()
        data = {'message': 'Email changed!', 'email': email}
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def forget_password(self, request):
        """User login."""
        serializer = ForgetPasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Account verification."""
        serializer = ResetPasswordSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Account verification."""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Verified account!'}
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def remove_card(self, request, *args, **kwargs):
        """Remove payment method"""
        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'

        remove = stripe.PaymentMethod.detach(
            request.data.get('payment_method').get('id'),
        )
        return HttpResponse(status=200)

    @action(detail=False, methods=['post'])
    def stripe_connect(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""
        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = StripeConnectSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def seller_add_payment_method(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = StripeSellerSubscriptionSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data
        stripe_customer_id = data['stripe_customer_id']

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_user(self, request, *args, **kwargs):
        if request.user.id == None:
            return Response(status=404)

        data = {
            'user': UserModelSerializer(request.user, many=False).data,

        }
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'

        stripe_customer_id = data['user']['stripe_customer_id']

        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data)

    @action(detail=False, methods=['post'])
    def get_user_by_email_jwt(self, request, *args, **kwargs):
        serializer = GetUserByJwtSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'

        stripe_customer_id = data['user']['stripe_customer_id']

        data['user']['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data)

    @action(detail=False, methods=['post'])
    def invite_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def list_contacts_available(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def seller_change_payment_method(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = SellerChangePaymentMethodSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data
        stripe_customer_id = data['stripe_customer_id']

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def list_invoices(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""
        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        subscriptions_queryset = PlanSubscription.objects.filter(user_plan_subscription=user, cancelled=False)
        if not subscriptions_queryset.exists():
            Response("User have not a plan subscription", status=status.HTTP_404_NOT_FOUND)
        subscription = subscriptions_queryset.first()
        list_data = stripe.Invoice.list(
            customer=user.stripe_customer_id,
            subscription=subscription.subscription_id
        )

        return Response(list_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def seller_cancel_subscription(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = SellerCancelSubscriptionSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data
        stripe_customer_id = data['stripe_customer_id']

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def seller_reactivate_subscription(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = SellerReactivateSubscriptionSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data
        stripe_customer_id = data['stripe_customer_id']

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def become_a_seller(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = BecomeASellerSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data
        stripe_customer_id = data['stripe_customer_id']

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def attach_payment_method(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        partial = request.method == 'PATCH'
        serializer = AttachPaymentMethodSerializer(
            user,
            data=request.data,
            context={"request": request, "stripe": stripe},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = UserModelSerializer(user, many=False).data
        stripe_customer_id = data['stripe_customer_id']

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def detach_payment_method(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
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

        data['payment_methods'] = helpers.get_payment_methods(stripe, stripe_customer_id)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def stripe_subscription_payment_failed(self, request, *args, **kwargs):
        """Process stripe webhook notification for subscription cancellation"""
        payload = request.body
        event = None

        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)

        if event.type == 'customer.subscription.deleted':
            invoice = event.data.object  # contains Stripe.invoice
            subscription_id = invoice.subscription

            try:
                stripe.Subscription.delete(subscription_id)
            except stripe.error.StripeError as e:
                return HttpResponse(status=400)

            except Exception as e:
                return HttpResponse(status=400)

            subscriptions_queryset = PlanSubscription.objects.filter(subscription_id=subscription_id, cancelled=False)
            if not subscriptions_queryset.exists():
                Response("User have not a plan subscription", status=status.HTTP_404_NOT_FOUND)
            subscription = subscriptions_queryset.first()

            user = subscription.user_plan_subscription
            subscription.update(
                cancelled=True
            )
            user.update(
                have_active_plan=False,
            )

            return HttpResponse(status=200)

        else:
            # Unexpected event type
            return HttpResponse(status=400)

    # Events that may have to handle:
    # - customer.subscription.trial_will_end - This event notify the subscription trial will end in one day

    @action(detail=False, methods=['post'])
    def stripe_webhook_subscription_cancelled(self, request, *args, **kwargs):
        """Process stripe webhook notification for subscription cancellation"""
        payload = request.body
        event = None
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51HCsUHIgGIa3w9CpMgSnYNk7ifsaahLoaD1kSpVHBCMKMueUb06dtKAWYGqhFEDb6zimiLmF8XwtLLeBt2hIvvW200YfRtDlPo'

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)

        # Handle the event
        if event.type == 'customer.subscription.deleted':
            subscription = event.data.object  # contains a stripe.Subscription
            subscriptions_queryset = PlanSubscription.objects.filter(subscription_id=subscription.id, cancelled=False)
            if not subscriptions_queryset.exists():
                Response("Plan subscription does not exist", status=status.HTTP_404_NOT_FOUND)
            plan_subscription = subscriptions_queryset.first()
            user = plan_subscription.user_plan_subscription
            plan_subscription.update(cancelled=True)
            user.update(have_active_plan=False)

            return HttpResponse(status=200)

        else:
            # Unexpected event type
            return HttpResponse(status=400)
