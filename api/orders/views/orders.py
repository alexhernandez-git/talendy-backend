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

# Serializers
from api.orders.serializers import OrderModelSerializer, AcceptOrderSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import os
from api.utils import helpers


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
        if user.seller_view:
            queryset = Order.objects.filter(seller=user)
        else:
            queryset = Order.objects.filter(buyer=user)

        return queryset

    def create(self, request, *args, **kwargs):
        """Process stripe connect auth flow."""

        user = request.user
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'

        serializer = AcceptOrderSerializer(
            data=request.data,
            context={"request": request, "stripe": stripe, "offer": request.data['offer']},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = OrderModelSerializer(user, many=False).data

        return Response(data, status=status.HTTP_200_OK)
