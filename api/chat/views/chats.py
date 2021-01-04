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
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.users.permissions import IsAccountOwner

# Models
from api.users.models import User
from api.chat.models import Chat, participants

# Serializers
from api.users.serializers import UserModelSerializer
from api.chat.serializers import ChatModelSerializer, CreateChatSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class ChatViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Chats view set."""

    queryset = Chat.objects.all()
    lookup_field = "id"
    serializer_class = ChatModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "participants__first_name",
        "participants__last_name",
        "participants__username",
    )

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "create":
            return CreateChatSerializer
        return ChatModelSerializer

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            return Chat.objects.filter(participants=user)
        return Chat.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()

        chat_data = ChatModelSerializer(chat, many=False).data

        headers = self.get_success_headers(chat)
        return Response(chat_data, status=status.HTTP_201_CREATED, headers=headers)