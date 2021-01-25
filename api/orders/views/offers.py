"""Users views."""

# Django
import pdb
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

# Models
from api.orders.models import Offer

# Serializers
from api.orders.serializers import OfferModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import os
from api.utils import helpers


class OfferViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Offer.objects.all()
    lookup_field = "id"
    serializer_class = OfferModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "title",
    )

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):
        """Restrict list to public-only."""
        user = self.request.user
        queryset = Offer.objects.filter(from_user=user)

        return queryset

    def create(self, request, *args, **kwargs):
        send_offer_by_email = request.data.get("send_offer_by_email", False)
        serializer = OfferModelSerializer(data=request.data, context={
            'request': request, 'send_offer_by_email': send_offer_by_email})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
