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
from api.chats.models import Chat, Message, MessageFile

# Serializers
from api.users.serializers import UserModelSerializer
from api.chats.serializers import (
    ChatModelSerializer,
    MessageModelSerializer,
    CreateMessageSerializer,
)


# Utils

from api.utils.mixins import AddChatMixin
import os
from api.utils import helpers
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
import base64


# Consumer methods
@sync_to_async
def create_message(self, text, sent_by, files):
    chat = Chat.objects.get(pk=self.room_name)
    user = User.objects.get(pk=sent_by["id"])
    new_message = Message.objects.create(chat=chat, text=text, sent_by=user)

    for i, file in enumerate(files):

        try:
            format, imgstr = file['file'].split(';base64,')

            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=file['name']+'.' + ext)
            MessageFile.objects.create(message=new_message, chat=chat, file=data, name=file['name'])
        except:
            files.pop(i)

    chat.last_message = new_message
    chat.save()
    return new_message, chat.pk, files


# Message ViewSet


class MessageViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    AddChatMixin,
):
    """Messages view set."""

    queryset = Message.objects.all()
    lookup_field = "id"
    serializer_class = MessageModelSerializer

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "create":
            return CreateMessageSerializer
        return MessageModelSerializer

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

        return Message.objects.filter(chat=self.chat)
