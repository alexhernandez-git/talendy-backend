# Django
from django.db.models import Q
from rest_framework.generics import get_object_or_404

# Django REST Framework
from rest_framework import serializers

# Models
from api.users.models import User
from api.chats.models import Chat, SeenBy, MessageFile
from api.notifications.models import NotificationUser

# Serializers
from api.users.serializers import UserModelSerializer

# Utils
from api.utils import helpers


class ChatModelSerializer(serializers.ModelSerializer):

    room_name = serializers.SerializerMethodField(read_only=True)
    picture = serializers.SerializerMethodField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    last_message_seen = serializers.SerializerMethodField(read_only=True)
    last_message_sent_by = serializers.SerializerMethodField(read_only=True)
    last_message_sent_by_username = serializers.SerializerMethodField(read_only=True)
    last_message_created = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = Chat
        fields = (
            "id",
            "room_name",
            "picture",
            "last_message",
            "created",
            "last_message_seen",
            "last_message_sent_by",
            "last_message_sent_by_username",
            "last_message_created"


        )

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

    def get_last_message_sent_by(self, obj):
        if obj.last_message:
            return obj.last_message.sent_by.pk

        return None

    def get_last_message_sent_by_username(self, obj):
        if obj.last_message:
            return obj.last_message.sent_by.username

        return None

    def get_last_message_created(self, obj):
        if obj.last_message:
            return obj.last_message.created

        return None


class RetrieveChatModelSerializer(serializers.ModelSerializer):

    room_name = serializers.SerializerMethodField(read_only=True)
    to_user = serializers.SerializerMethodField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    last_message_seen = serializers.SerializerMethodField(read_only=True)
    last_message_sent_by = serializers.SerializerMethodField(read_only=True)
    last_message_sent_by_username = serializers.SerializerMethodField(read_only=True)
    last_message_created = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = Chat
        fields = (
            "id",
            "room_name",
            "to_user",
            "last_message",
            "created",
            "last_message_seen",
            "last_message_sent_by",
            "last_message_sent_by_username",
            "last_message_created"
        )

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

    def get_last_message_sent_by(self, obj):
        if obj.last_message:
            return obj.last_message.sent_by.pk

        return None

    def get_last_message_sent_by_username(self, obj):
        if obj.last_message:
            return obj.last_message.sent_by.username

        return None

    def get_last_message_created(self, obj):
        if obj.last_message:
            return obj.last_message.created

        return None


class CreateChatSerializer(serializers.Serializer):
    to_user = serializers.CharField()

    def validate(self, data):
        to_user = get_object_or_404(User, pk=data["to_user"])
        from_member = self.context["request"].user

        chats = Chat.objects.filter(participants=from_member)
        chats = chats.filter(participants=to_user)

        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    return {"chat": chat}
            raise serializers.ValidationError("Chat not found")
        return {"to_user": to_user, "from_member": from_member}

    def create(self, validated_data):
        if "chat" in validated_data:
            return {"chat": validated_data["chat"], "status": "retrieved"}

        to_user = validated_data["to_user"]
        from_member = validated_data["from_member"]
        chat = Chat.objects.create()

        chat.participants.add(to_user)
        chat.participants.add(from_member)
        chat.save()

        return {"chat": chat, "status": "created"}


class ClearChatNotification(serializers.Serializer):

    def update(self, instance, validated_data):
        chat = validated_data["chat"]
        user = self.context['request'].user
        user.pending_notifications = False
        user.pending_messages = False
        notifications = NotificationUser.objects.filter(
            portal=chat.portal, notification__chat=instance, is_read=False, user=user)

        for notification in notifications:
            notification.is_read = True
            notification.save()

        user.save()

        return instance
