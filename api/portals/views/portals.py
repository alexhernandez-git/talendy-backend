"""Users views."""

# Django
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
from api.portals.serializers import PortalModelSerializer, CreatePortalSerializer
from api.users.serializers import UserModelSerializer

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
    mixins.CreateModelMixin,
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

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['create']:
            return CreatePortalSerializer
        return PortalModelSerializer

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
        request.data['username'] = helpers.get_random_username()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.save()

        data = {
            "user": UserModelSerializer(data['user']).data,
            "access_token": data['access_token']
        }
        return Response(data, status=status.HTTP_201_CREATED)
