# Django
from django.db.models import Q
from rest_framework.generics import get_object_or_404

# Django REST Framework
from rest_framework import serializers

# Models
from api.users.models import User
from api.chats.models import Chat, SeenBy
from api.notifications.models import NotificationUser

# Serializers
from api.users.serializers import UserModelSerializer


class ChatModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    room_name = serializers.SerializerMethodField(read_only=True)
    picture = serializers.SerializerMethodField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    last_message_seen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Chat
        fields = ("id", "room_name", "picture", "last_message", "created", "last_message_seen")

        read_only_fields = ("id",)

    def get_room_name(self, obj):
        if obj.room_name:
            return obj.room_name
        user = self.context["request"].user
        to_users = obj.participants.all().exclude(pk=user.pk)
        if to_users.exists():
            return to_users[0].username
        return None

    def get_picture(self, obj):
        user = self.context["request"].user
        to_users = obj.participants.all().exclude(pk=user.pk)
        if to_users.exists() and to_users[0].picture:
            return to_users[0].picture.url
        return None

    def get_last_message(self, obj):

        if obj.last_message:

            return obj.last_message.text

        return None

    def get_last_message_seen(self, obj):
        user = self.context["request"].user
        if obj.last_message:
            if obj.last_message.sent_by == user:
                return True

            seen_by = SeenBy.objects.filter(chat=obj, user=user)
            if seen_by.exists():
                seen_by = seen_by[0]

                return seen_by.message == obj.last_message
            return False
        else:
            return True


class RetrieveChatModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    room_name = serializers.SerializerMethodField(read_only=True)
    to_user = serializers.SerializerMethodField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    last_message_seen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Chat
        fields = ("id", "room_name", "to_user", "last_message", "created", "last_message_seen")

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

    def get_last_message(self, obj):

        if obj.last_message:

            return obj.last_message.text

        return None

    def get_last_message_seen(self, obj):
        user = self.context["request"].user
        to_users = obj.participants.all().exclude(pk=user.pk)
        if to_users.exists():
            to_user = to_users[0]

            if obj.last_message and obj.last_message.sent_by == to_user:
                seen_by = SeenBy.objects.filter(chat=obj, user=to_user)
                if seen_by.exists():
                    seen_by = seen_by[0]
                    return seen_by.message == obj.last_message

        return False


class CreateChatSerializer(serializers.Serializer):
    to_user = serializers.CharField()

    def validate(self, data):
        to_user = get_object_or_404(User, pk=data["to_user"])
        from_user = self.context["request"].user

        chats = Chat.objects.filter(participants=from_user)
        chats = chats.filter(participants=to_user)

        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    return {"chat": chat}
            raise serializers.ValidationError("Chat not found")
        return {"to_user": to_user, "from_user": from_user}

    def create(self, validated_data):
        if "chat" in validated_data:
            return {"chat": validated_data["chat"], "status": "retrieved"}

        to_user = validated_data["to_user"]
        from_user = validated_data["from_user"]
        chat = Chat.objects.create()

        chat.participants.add(to_user)
        chat.participants.add(from_user)
        chat.save()

        return {"chat": chat, "status": "created"}


class ClearChatNotification(serializers.Serializer):

    def update(self, instance, validated_data):
        user = self.context['request'].user
        notifications = NotificationUser.objects.filter(notification__chat=instance, is_read=False, user=user)

        for notification in notifications:
            notification.is_read = True
            notification.save()
        return instance
