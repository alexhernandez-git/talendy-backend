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
from api.chats.models import Chat

# Serializers
from api.users.serializers import UserModelSerializer
from api.chats.serializers import (
    ChatModelSerializer,
    CreateChatSerializer,
    RetrieveChatModelSerializer,
    CreateSeenBySerializer,
    ClearChatNotification
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from api.utils import helpers


class ChatViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Chats view set."""

    queryset = Chat.objects.all()
    lookup_field = "id"
    serializer_class = ChatModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    pagination_class = None
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
        elif self.action == "retrieve":
            return RetrieveChatModelSerializer
        return ChatModelSerializer

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            return Chat.objects.filter(participants=user).exclude(last_message=None)
        return Chat.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Create seen by
        createSeenSerializer = CreateSeenBySerializer(
            data={}, context={"request": request, "chat": instance}
        )
        is_valid = createSeenSerializer.is_valid(raise_exception=False)
        if is_valid:
            createSeenSerializer.save()

        # Clear chat notifications
        clearChatNotification = ClearChatNotification(
            instance,
            data={},
            context={"request": request, "chat": instance},
            partial=True
        )
        is_valid = clearChatNotification.is_valid(raise_exception=False)
        if is_valid:
            clearChatNotification.update(instance, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        chat_data = ChatModelSerializer(
            result["chat"], context={"request": request}, many=False
        ).data

        headers = self.get_success_headers(result["chat"])
        current_status = None
        if result["status"] == "retrieved":
            current_status = status.HTTP_200_OK
        else:
            current_status = status.HTTP_201_CREATED

        return Response(chat_data, status=current_status, headers=headers)

    @action(detail=True, methods=['get'])
    def retrieve_chat_feed(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
