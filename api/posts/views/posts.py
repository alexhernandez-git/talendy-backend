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
from api.posts.models import Post, PostMember
from api.users.models import Follow, User

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
    filterset_fields = ['community']
    search_fields = (
        "title",
        "text",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

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
        queryset = Post.objects.all()

        if self.action == "list":

            queryset = Post.objects.filter(status=Post.ACTIVE)
        elif self.action == "list_most_karma_posts":
            queryset = Post.objects.filter(status=Post.ACTIVE).order_by('-karma_offered')
        elif self.action == "list_followed_users_posts":
            user = self.request.user
            queryset = Post.objects.filter(
                status=Post.ACTIVE, user__id__in=Follow.objects.filter(from_user=user).values_list(
                    'followed_user'))
        elif self.action == "list_my_posts":
            user = self.request.user
            queryset = Post.objects.filter(user=user)
        elif self.action == "list_my_active_posts":
            user = self.request.user
            queryset = Post.objects.filter(user=user, status=Post.ACTIVE)
        elif self.action == "list_my_solved_posts":
            user = self.request.user
            queryset = Post.objects.filter(user=user, status=Post.SOLVED)
        elif self.action == "list_contributed_posts":
            user = self.request.user
            queryset = Post.objects.filter(members=user).exclude(user=user)
        elif self.action == "list_contributed_active_posts":
            user = self.request.user
            queryset = Post.objects.filter(members=user, status=Post.ACTIVE).exclude(user=user)
        elif self.action == "list_contributed_solved_posts":
            user = self.request.user
            queryset = Post.objects.filter(members=user, status=Post.SOLVED).exclude(user=user)

        elif self.action == "list_user_contributed":
            user = get_object_or_404(User, id=self.kwargs['id'])
            queryset = Post.objects.filter(members=user).exclude(user=user)

        elif self.action == "list_user_posts":
            user = get_object_or_404(User, id=self.kwargs['id'])
            queryset = Post.objects.filter(user=user)
        return queryset

    @action(detail=False, methods=['get'])
    def list_most_karma_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_followed_users_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_my_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_my_active_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_my_solved_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_contributed_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_contributed_active_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_contributed_solved_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_user_contributed(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_user_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
