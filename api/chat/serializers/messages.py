# Django REST Framework
from rest_framework import serializers

# Models
from api.chat.models import Message


class MessageModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Message
        fields = ("id", "text", "sent_by")

        read_only_fields = ("id",)
