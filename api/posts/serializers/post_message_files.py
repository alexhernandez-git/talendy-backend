# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import Message, Chat, MessageFile

# Serializers


class MessageFileModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = MessageFile
        fields = ("id", "file", "name")

        read_only_fields = ("id",)
