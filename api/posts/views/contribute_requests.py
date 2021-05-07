"""Users views."""

# Django
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import F

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
from api.users.permissions import IsAccountOwner

# Models
from api.posts.models import ContributeRequest

# Serializers
from api.posts.serializers import (
    ContributeRequestModelSerializer,
    RequestContributeSerializer,
    AcceptContributeRequestSerializer,
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class ContributeRequestViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = ContributeRequest.objects.all()
    lookup_field = "id"
    serializer_class = ContributeRequestModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "create":
            return RequestContributeSerializer

        return ContributeRequestModelSerializer

    def get_queryset(self):
        """Restrict list to public-only."""
        user = self.request.user
        queryset = ContributeRequest.objects.filter(post__user=user)

        return queryset

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contribute_request = serializer.save()
        contribute_request_data = ContributeRequestModelSerializer(contribute_request, many=False).data
        headers = self.get_success_headers(serializer.data)
        return Response(contribute_request_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'])
    def accept(self, request, *args, **kwargs):

        contribute_request = get_object_or_404(ContributeRequest, id=kwargs['id'])

        partial = request.method == 'PATCH'
        serializer = AcceptContributeRequestSerializer(
            contribute_request,
            data=request.data,
            context={"request": request},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)