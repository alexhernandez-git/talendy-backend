# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import Message, Chat

# Serializers
from api.activities.serializers import ActivityModelSerializer


class MessageModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    sent_by = serializers.SerializerMethodField(read_only=True)
    activity = ActivityModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Message
        fields = ("id", "text", "sent_by", "created", "activity")

        read_only_fields = ("id",)

    def get_sent_by(self, obj):
        from api.users.serializers import UserModelSerializer

        return UserModelSerializer(obj.sent_by, many=False).data


class CreateMessageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000)

    def create(self, validated_data):

        user = self.context["request"].user
        chat = self.context["chat"]

        message = Message.objects.create(chat=chat, text=validated_data["text"], sent_by=user)
        chat.last_message = message
        chat.save()
        return message
