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
from api.posts.permissions import IsPostOwner

# Models
from api.posts.models import Post

# Serializers
from api.posts.serializers import PostModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class PostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Post.objects.all()
    lookup_field = "id"
    serializer_class = PostModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['create']:
            permissions = [IsAuthenticated]
        elif self.action in ['update']:
            permissions = [IsPostOwner, IsAuthenticated]
        else:
            permissions = []
        return [p() for p in permissions]

    def get_queryset(self):
        """Restrict list to public-only."""
        queryset = Post.objects.filter(status=Post.ACTIVE)

        return queryset

    def create(self, request, *args, **kwargs):

        serializer = PostModelSerializer(data=request.data, context={
                                         "request": request, "images": request.data.getlist('images')})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = PostModelSerializer(
            post, data=request.data,
            context={"request": request, "images": request.data.getlist('images'),
                     "current_images": request.data['current_images']},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
