# Django
from django.db.models import Q

# Django REST Framework
from rest_framework import serializers

# Models
from api.users.models import User
from api.chat.models import Chat, participants

# Serializers
from api.users.serializers import UserModelSerializer


class ChatModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    room_name = serializers.SerializerMethodField(read_only=True)
    to_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Chat
        fields = ("id", "room_name", "to_user", "last_message")

        read_only_fields = ("id",)

    def get_room_name(self, obj):
        if obj.room_name:
            return obj.room_name
        user = self.context["request"].user
        to_users = obj.participants.all().exclude(pk=user.pk)
        if to_users.exists():
            return to_users[0].username
        return None

    def get_to_user(self, obj):
        user = self.context["request"].user
        to_users = obj.participants.all().exclude(pk=user.pk)
        if to_users.exists():
            return UserModelSerializer(to_users[0], many=False).data
        return None


class CreateChatSerializer(serializers.Serializer):
    to_user = serializers.CharField()

    def validate(self, data):
        to_user = User.objects.get(pk=data["to_user"])
        from_user = self.context["request"].user

        chats = Chat.objects.filter(Q(participants=to_user) and Q(participants=from_user))

        if chats.exists():
            raise serializers.ValidationError("You already have this chat")
        return {"to_user": to_user, "from_user": from_user}

    def create(self, validated_data):
        to_user = validated_data["to_user"]
        from_user = validated_data["from_user"]
        chat = Chat.objects.create()

        chat.participants.add(to_user)
        chat.participants.add(from_user)
        chat.save()

        return chat
