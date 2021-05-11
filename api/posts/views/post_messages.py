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
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.users.permissions import IsAccountOwner


# Models
from api.users.models import User
from api.posts.models import Post, PostMessage, PostMessageFile

# Serializers
from api.users.serializers import UserModelSerializer
from api.posts.serializers import (
    PostMessageModelSerializer,
    CreatePostMessageSerializer,
)


# Utils

from api.utils.mixins import AddPostMixin
import os
from api.utils import helpers
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
import base64


class PostMessageViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    AddPostMixin,
):
    """Messages view set."""

    queryset = PostMessage.objects.all()
    lookup_field = "id"
    serializer_class = PostMessageModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action == "create":
            return CreatePostMessageSerializer
        return PostMessageModelSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "post": self.post_object,
        }

    def get_queryset(self):

        return PostMessage.objects.filter(post=self.post_object)
