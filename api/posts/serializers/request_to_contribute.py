"""Notifications serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer
from api.chats.serializers import MessageModelSerializer

# Models
from api.users.models import User
from api.posts.models import Post


class PostModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    actor = UserModelSerializer(read_only=True)
    messages = serializers.SerializerMethodField(read_only=True)
    is_chat_notification = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Post
        fields = (
            "id",
            "type",
            "actor",
            "messages",
            "modified",
        )

        read_only_fields = ("id",)

    def get_messages(self, obj):
        return MessageModelSerializer(obj.messages, many=True).data
