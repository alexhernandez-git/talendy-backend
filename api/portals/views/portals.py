"""Users views."""

# Django
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
from api.portals.models import Portal

# Serializers
from api.portals.serializers import PortalModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class PortalViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Portal.objects.all()
    lookup_field = "id"
    serializer_class = PortalModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['create']:
            permissions = [AllowAny]
        elif self.action in ['']:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]
