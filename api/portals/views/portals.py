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

# Models
from api.portals.models import Portal

# Serializers
from api.portals.serializers import PortalModelSerializer, CreatePortalSerializer, IsNameAvailableSerializer, IsUrlAvailableSerializer, PortalListModelSerializer
from api.users.serializers import UserModelSerializer, DetailedUserModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Utils
import os
from api.utils import helpers
import stripe
import environ
env = environ.Env()


class PortalViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
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

        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['create']:
            return CreatePortalSerializer
        if self.action in ['list']:
            return PortalListModelSerializer
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
