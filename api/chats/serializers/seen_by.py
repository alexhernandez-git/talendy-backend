# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import SeenBy

# Serializers
from api.users.serializers import UserModelSerializer


class SeenByModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = SeenBy
        fields = ("id", "chat", "message", "participant")

        read_only_fields = ("id",)


class CreateSeenBySerializer(serializers.Serializer):
    def validate(self, data):
        chat = self.context["chat"]
        if not chat.last_message:
            raise serializers.ValidationError("Not have last message")

    def create(self, validated_data):

        user = self.context["request"].user
        chat = self.context["chat"]
        seen_by = SeenBy.objects.filter(chat=chat, sent_by=user)[0]
        if seen_by.message != chat.last_message:
            seen_by.delete()
            seen_by = SeenBy.objects.create(chat=chat, message=chat.last_message, sent_by=user)

        return seen_by