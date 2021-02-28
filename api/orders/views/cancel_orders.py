"""Users views."""

# Django
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from api.utils.mixins import AddOrderMixin
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.orders.permissions import IsPartOfOrder

# Models
from api.orders.models import CancelOrder

# Serializers
from api.orders.serializers import (
    CancelOrderModelSerializer,
    CancelOrderCancelationModelSerializer,
    AcceptOrderCancelationModelSerializer,
    UnsubscribeOrderModelSerializer
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import os
from api.utils import helpers
import stripe


class CancelOrderViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    AddOrderMixin,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = CancelOrder.objects.all()
    lookup_field = "id"
    serializer_class = CancelOrderModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""
        # if self.action in ['retrieve']:
        #     permissions = []
        # else:
        permissions = [IsAuthenticated, IsPartOfOrder]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['cancel_order_cancelation']:
            return CancelOrderCancelationModelSerializer
        elif self.action in ['accept_order_cancelation']:
            return AcceptOrderCancelationModelSerializer
        return CancelOrderModelSerializer

    def create(self, request, *args, **kwargs):

        serializer = CancelOrderModelSerializer(data=request.data,
                                                context={
                                                    'order': self.order,
                                                    'request': request,
                                                })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'])
    def cancel_order_cancelation(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def accept_order_cancelation(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def unsubscribe_order(self, request, *args, **kwargs):
        if 'STRIPE_API_KEY' in os.environ:
            stripe.api_key = os.environ['STRIPE_API_KEY']
        else:
            stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        serializer = UnsubscribeOrderModelSerializer(data=request.data,
                                                     context={
                                                         'order': self.order,
                                                         'stripe': stripe,
                                                         'request': request,
                                                     })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
