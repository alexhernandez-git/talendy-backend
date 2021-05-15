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
from api.users.models import Review

# Serializers
from api.users.serializers import ReviewModelSerializer, WithdrawFundsModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class ReviewViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Review.objects.all()
    lookup_field = "id"
    serializer_class = ReviewModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):
        """Restrict list to public-only."""
        user = self.request.user

        queryset = Review.objects.filter(reviewd_user=user)
        return queryset
