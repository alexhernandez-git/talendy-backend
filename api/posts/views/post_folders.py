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
from api.posts.models import PostFolder

# Serializers
from api.posts.serializers import (
    PostFolderModelSerializer,
    MovePostFoldersSerializer

)


import stripe

# Utils
from api.utils.mixins import AddPostMixin


class PostFolderViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        AddPostMixin):

    """Circle view set."""
    pagination_class = None
    serializer_class = PostFolderModelSerializer
    lookup_field = 'pk'
    queryset = PostFolder.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Restrict list to public-only."""
        queryset = PostFolder.objects.filter(post=self.post_object)
        return queryset

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

        serializer = PostFolderModelSerializer(
            data=request.data,
            context={
                'post': post,
                'request': request,
                'top_folder': top_folder},
        )
        serializer.is_valid(raise_exception=True)
        folder = serializer.save()

        data = PostFolderModelSerializer(folder, many=False).data

        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        folder = self.get_object()
        post = self.post_object
        partial = request.method == 'PATCH'

        serializer = PostFolderModelSerializer(
            folder,
            data=request.data,
            context={
                'post': post,
                'request': request
            },
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        folder = serializer.save()

        data = PostFolderModelSerializer(folder).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put', 'patch'])
    def update_top_folder(self, request, *args, **kwargs):
        folder = self.get_object()
        partial = request.method == 'PATCH'

        serializer = MovePostFoldersSerializer(
            folder,
            data=request.data,
            context={
                'request': request
            },
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        folder = serializer.save()

        data = PostFolderModelSerializer(folder).data
        return Response(data, status=status.HTTP_200_OK)
