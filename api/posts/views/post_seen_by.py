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
from api.posts.models import PostSeenBy, PostSeenBy

# Serializers
from api.users.serializers import UserModelSerializer
from api.posts.serializers import (
    PostSeenByModelSerializer,
    PostSeenByModelSerializer,
    CreatePostSeenBySerializer,
)


# Utils

from api.utils.mixins import AddChatMixin
import os
from api.utils import helpers


class PostSeenByViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    AddChatMixin,
):
    """PostSeenBy view set."""

    queryset = PostSeenBy.objects.all()
    lookup_field = "id"
    serializer_class = PostSeenByModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "create":
            return CreatePostSeenBySerializer
        return PostSeenByModelSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "chat": self.chat,
        }

    def get_queryset(self):

        return PostSeenBy.objects.filter(chat=self.chat)
