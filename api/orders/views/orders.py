"""Users views."""

# Django
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
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
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

# Models
from api.orders.models import Order
from api.activities.models import Activity

# Serializers
from api.orders.serializers import OrderModelSerializer, AcceptOrderSerializer
from api.activities.serializers import ActivityModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import os
from api.utils import helpers
import environ
env = environ.Env()


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Order.objects.all()
    lookup_field = "id"
    serializer_class = OrderModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "title",
        "seller__username",
        "seller__first_name",
        "seller__last_name",
        "seller__email",
        "buyer__username",
        "buyer__first_name",
        "buyer__last_name",
        "buyer__email",
    )

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):
        """Restrict list to public-only."""
        user = self.request.user
        queryset = self.queryset
        if user.seller_view:
            queryset = Order.objects.filter(seller=user)
        else:
            queryset = Order.objects.filter(buyer=user)

        if self.action == "active_orders":
            return queryset.filter(status=Order.ACTIVE)[:10]
        if self.action == "completed_orders":
            return queryset.filter(status=Order.DELIVERED)[:10]
        if self.action == "cancelled_orders":
            return queryset.filter(status=Order.CANCELLED)[:10]
        if self.action == "list_activities":

            order = get_object_or_404(Order, id=self.kwargs['id'])
            return Activity.objects.filter(order=order)
        return queryset

    def create(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in env:
            stripe.api_key = env('STRIPE_API_KEY')
        else:
            stripe.api_key = 'sk_test_51IZy28Dieqyg7vAImOKb5hg7amYYGSzPTtSqoT9RKI69VyycnqXV3wCPANyYHEl2hI7KLHHAeIPpC7POg7I4WMwi00TSn067f4'

        serializer = AcceptOrderSerializer(
            data=request.data,
            context={"request": request, "stripe": stripe, "offer": request.data['offer']},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        data = OrderModelSerializer(order, many=False).data

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def active_orders(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed_orders(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cancelled_orders(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_activities(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = ActivityModelSerializer(queryset, many=True)
        return Response(serializer.data)
