"""Users views."""

# Django
from typing import OrderedDict
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.portals.permissions import IsAdminOrManager

# Models
from api.portals.models import Portal, PlanSubscription, PlanPayment
from api.plans.models import Plan

# Serializers
from api.portals.serializers import (
    PortalModelSerializer, CreatePortalSerializer, IsNameAvailableSerializer, IsUrlAvailableSerializer,
    ChangePlanSerializer, PortalListModelSerializer, AddBillingInformationSerializer, ChangePaymentMethodSerializer)
from api.users.serializers import UserModelSerializer, DetailedUserModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Utils
import os
from api.utils import helpers
import stripe
import environ
import json
import tldextract
env = environ.Env()


class PortalViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Portal.objects.all()
    lookup_field = "url"
    serializer_class = PortalModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "name",
        "url",

    )

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = []

        if self.action in ['create', 'is_name_available', 'is_url_available', 'retrieve']:
            permissions = [AllowAny]
        elif self.action in ['list']:
            permissions = [IsAuthenticated]
        elif self.action in ['update']:
            permissions = [IsAdminOrManager]

        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['create']:
            return CreatePortalSerializer
        elif self.action in ['list']:
            return PortalListModelSerializer
        elif self.action in ['add_billing_information']:
            return AddBillingInformationSerializer
        elif self.action in ['change_payment_method']:
            return ChangePaymentMethodSerializer
        elif self.action in ['change_plan']:
            return ChangePlanSerializer
        return PortalModelSerializer

    def get_queryset(self):
        queryset = Portal.objects.all()
        if self.action == 'list':
            queryset = Portal.objects.filter(members=self.request.user)

        return queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51HCopMKRJ23zrNRsBClyDiNSIItLH6jxRjczuqwvtXRnTRTKIPAPMaukgGr3HA9PjvCPwC8ZJ5mjoR7mq18od40S00IgdsI8TG'
        if self.action in ['create']:
            return {
                "request": self.request,
                "format": self.format_kwarg,
                "view": self,
                "stripe": stripe,
            }

        else:
            return {
                "request": self.request,
                "format": self.format_kwarg,
                "view": self,
                "stripe": stripe,
            }

    def create(self, request, *args, **kwargs):

        data = OrderedDict()
        data.update(request.data)
        if not request.user.id:
            data['username'] = helpers.get_random_username()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        data = serializer.save()

        data = {
            "portal": PortalModelSerializer(data['portal']).data,
            "user": DetailedUserModelSerializer(data['user']).data,
            "access_token": data['access_token']
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'])
    def add_billing_information(self, request, *args, **kwargs):

        partial = request.method == 'PATCH'
        subdomain = tldextract.extract(request.META['HTTP_ORIGIN']).subdomain

        portal = get_object_or_404(Portal, url=subdomain)
        serializer = self.get_serializer(
            portal,
            data=request.data,
            partial=partial)

        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        # Return Portal and also the user payment methods
        data = {
            "payment_methods": helpers.get_payment_methods(stripe, request.user.stripe_customer_id),
            "portal": PortalModelSerializer(data).data
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def change_payment_method(self, request, *args, **kwargs):

        partial = request.method == 'PATCH'
        subdomain = tldextract.extract(request.META['HTTP_ORIGIN']).subdomain

        portal = get_object_or_404(Portal, url=subdomain)
        serializer = self.get_serializer(
            portal,
            data=request.data,
            partial=partial)

        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        # Return Portal and also the user payment methods
        data = PortalModelSerializer(data).data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def is_name_available(self, request):
        """Check if name passed is correct."""
        serializer = IsNameAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        name = serializer.data
        return Response(data=name, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def is_url_available(self, request):
        """Check if url passed is correct."""
        serializer = IsUrlAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        url = serializer.data
        return Response(data=url, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def change_plan(self, request, *args, **kwargs):

        partial = request.method == 'PATCH'
        subdomain = tldextract.extract(request.META['HTTP_ORIGIN']).subdomain

        portal = get_object_or_404(Portal, url=subdomain)
        serializer = self.get_serializer(
            portal,
            data=request.data,
            partial=partial)

        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        # Return Portal and also the user payment methods
        data = PortalModelSerializer(data).data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def stripe_webhooks_invoice_payment_succeeded(self, request, *args, **kwargs):
        """Process stripe webhook notification for subscription cancellation"""
        payload = request.body
        event = None
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51IZy28Dieqyg7vAImOKb5hg7amYYGSzPTtSqoT9RKI69VyycnqXV3wCPANyYHEl2hI7KLHHAeIPpC7POg7I4WMwi00TSn067f4'

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        print(event)
        # Handle the event
        if event.type == 'invoice.payment_succeeded':
            invoice_success = event.data.object
            invoice_id = invoice_success['id']
            charge_id = invoice_success['charge']
            invoice_pdf = invoice_success['invoice_pdf']
            subscription_id = invoice_success['subscription']
            amount_paid = float(invoice_success['amount_paid']) / 100
            currency = invoice_success['currency']
            status = invoice_success['status']

            # Get plan subscription
            plan_subscriptions = PlanSubscription.objects.filter(subscription_id=subscription_id)
            if plan_subscriptions.exists():
                plan_subscription = plan_subscriptions.first()
                plan_user = plan_subscription.user
                plan_portal = plan_subscription.portal

                PlanPayment.objects.create(
                    user=plan_user,
                    portal=plan_portal,
                    invoice_id=invoice_id,
                    subscription=plan_subscription,
                    invoice_pdf=invoice_pdf,
                    charge_id=charge_id,
                    amount_paid=amount_paid,
                    currency=currency,
                    status=status,
                )
                if plan_portal.free_trial_invoiced:

                    def create_new_price():
                        price = stripe.Price.create(
                            unit_amount=int(plan_subscription.plan_unit_amount * 100),
                            currency=plan_subscription.plan_currency,
                            product=product_id,
                            recurring={"interval": "month"},
                        )

                        subscription = stripe.Subscription.retrieve(
                            subscription_id)

                        stripe.Subscription.modify(
                            subscription_id,
                            cancel_at_period_end=False,
                            proration_behavior=None,
                            items=[
                                {
                                    'id': subscription['items']['data'][0]['id'],
                                    "price": price['id']
                                },
                            ],
                        )
                    product_id = plan_subscription.product_id
                    plan_currency = plan_subscription.plan_currency
                    plan_type = plan_subscription.plan_type
                    plan_interval = plan_subscription.plan_interval

                    plans = Plan.objects.filter(stripe_product_id=product_id,
                                                currency=plan_currency, type=plan_type, interval=plan_interval)
                    if plans.exists():
                        plan = plans.first()
                        if plan.unit_amount != plan_subscription.plan_unit_amount:
                            create_new_price()
                        else:

                            subscription = stripe.Subscription.retrieve(
                                subscription_id)

                            stripe.Subscription.modify(
                                subscription_id,
                                cancel_at_period_end=False,
                                proration_behavior=None,
                                items=[
                                    {
                                        'id': subscription['items']['data'][0]['id'],
                                        "price": plan.stripe_price_id
                                    },
                                ],
                            )

                            # If plan does not exists
                    else:
                        create_new_price()
                else:
                    # enter the free trial invocie
                    plan_portal.free_trial_invoiced = True
                    plan_portal.save()
        return HttpResponse(status=200)
