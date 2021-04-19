"""Users views."""

# Django
import pdb
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
from api.users.models import Follow

# Serializers
from api.users.serializers import FollowModelSerializer, CreateFollowSerializer, UnfollowSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Follow.objects.all()
    lookup_field = "id"
    serializer_class = FollowModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "follow_user__first_name",
        "follow_user__last_name",
        "follow_user__username",
        "follow_user__email",
    )

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):
        """Restrict list to public-only."""

        user = self.request.user
        queryset = Follow.objects.filter(from_user=user)

        return queryset

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "create":
            return CreateFollowSerializer
        if self.action == "unfollow":
            return UnfollowSerializer
        return FollowModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        follow = serializer.save()
        follow_data = FollowModelSerializer(follow, many=False).data
        headers = self.get_success_headers(serializer.data)
        return Response(follow_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def unfollow(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
