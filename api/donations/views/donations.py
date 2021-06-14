"""Users views."""

# Django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from config.settings.base import env

# Django REST Framework
from api.users.models import User
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
from api.users.permissions import IsAccountOwner

# Models
from api.donations.models import Donation

# Serializers
from api.donations.serializers import DonationModelSerializer
from api.users.serializers import DetailedUserModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers
import stripe


class DonationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Donation.objects.all()
    lookup_field = "id"
    serializer_class = DonationModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permissions = [IsAuthenticated]
        else:
            permissions = []
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        return DonationModelSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """

        context = {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }

        return context

    def get_queryset(self):
        """Restrict list to public-only."""
        if self.action in ['list', 'retrieve']:
            user = self.request.user

            queryset = Donation.objects.filter(to_user=user)
        else:
            queryset = Donation.objects.all()

        return queryset
