"""Program views."""

# Django REST Framework
from rest_framework import mixins, viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Permissions
from rest_framework.permissions import IsAuthenticated

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


# Models
from api.posts.models import PostFile

# Serializers
from api.posts.serializers import (
    PostFileModelSerializer,
    MovePostFilesSerializer
)

from api.users.serializers import (
    UserModelSerializer,
)

import stripe

# Utils
from api.utils.mixins import AddPostMixin


class PostFileViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      AddPostMixin):

    """Circle view set."""
    pagination_class = None
    serializer_class = PostFileModelSerializer
    lookup_field = 'pk'
    queryset = PostFile.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        """Restrict list to public-only."""
        queryset = PostFile.objects.filter(post=self.post_object)
        return queryset

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]

        return [permission() for permission in permissions]

    def list(self, request, *args, **kwargs):
        if 'top_folder' in request.GET and request.GET['top_folder']:
            queryset = self.get_queryset().filter(
                top_folder=request.GET['top_folder'])
        else:
            queryset = self.get_queryset().filter(
                top_folder=None)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Call by owners to finish a ride."""

        post = self.post_object
        if 'top_folder' in request.data:
            top_folder = request.data['top_folder']
        else:
            top_folder = None
        serializer = PostFileModelSerializer(
            data=request.data,
            context={
                'post': post,
                'top_folder': top_folder},
        )
        serializer.is_valid(raise_exception=True)
        file = serializer.save()

        data = PostFileModelSerializer(file, many=False).data

        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        file = self.get_object()
        post = self.post_object
        partial = request.method == 'PATCH'

        serializer = PostFileModelSerializer(
            file,
            data=request.data,
            context={
                'post': post,
                'request': request
            },
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        file = serializer.save()

        data = PostFileModelSerializer(file).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put', 'patch'])
    def update_top_folder(self, request, *args, **kwargs):
        file = self.get_object()
        partial = request.method == 'PATCH'

        serializer = MovePostFilesSerializer(
            file,
            data=request.data,
            context={
                'request': request
            },
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        file = serializer.save()

        data = PostFileModelSerializer(file).data
        return Response(data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        post = instance.post
        size = instance.size

        # Delete the instance
        instance.delete()
        post.files_size -= size
        post.save()
