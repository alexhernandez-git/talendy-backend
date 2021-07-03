"""Users views."""

# Django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
from api.users.models import User
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
from api.users.permissions import IsAccountOwner

# Models
from api.portals.models import PortalMember, Portal

# Serializers
from api.portals.serializers import PortalMemberModelSerializer, CreatePortalMemberSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Helpers

import os
from api.utils import helpers
import tldextract


class PortalMemberViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = PortalMember.objects.all()
    lookup_field = "id"
    serializer_class = PortalMemberModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['create']:
            return CreatePortalMemberSerializer

        return PortalMemberModelSerializer

    def get_queryset(self):
        """Restrict list to public-only."""
        subdomain = tldextract.extract(self.request.META['HTTP_ORIGIN']).subdomain
        portal = get_object_or_404(Portal, url=subdomain)

        queryset = PortalMember.objects.filter(portal=portal)

        return queryset

    def create(self, request, *args, **kwargs):
        data = []
        for data in request.data:

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)

            data = serializer.save()

            data.append(PortalMemberModelSerializer(data).data)

        return Response(data, status=status.HTTP_201_CREATED)
