# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import MessageFile

# Serializers


class MessageFileModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = MessageFile
        fields = ("id", "file", "name")

        read_only_fields = ("id",)
