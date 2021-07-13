# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import SeenBy

# Serializers
from api.users.serializers import UserModelSerializer


class SeenByModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = SeenBy
        fields = ("id", "chat", "message", "user", "modified")

        read_only_fields = ("id",)


class CreateSeenBySerializer(serializers.Serializer):
    def validate(self, data):
        chat = self.context["chat"]

        if not chat.last_message:
            raise serializers.ValidationError("Not have last message")
        return data

    def create(self, validated_data):

        user = self.context["request"].user
        chat = self.context["chat"]

        seen_by, created = SeenBy.objects.get_or_create(chat=chat, user=user)
        if seen_by.message != chat.last_message:

            seen_by.message = chat.last_message
            seen_by.save()
        return seen_by
