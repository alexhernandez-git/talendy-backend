"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Revision, Order
from api.activities.models import Activity, RevisionActivity
from api.users.models import User
from api.chats.models import Message, Chat, SeenBy

# Serializers
from api.orders.serializers import OrderModelSerializer
from api.users.serializers import UserModelSerializer


class RevisionModelSerializer(serializers.ModelSerializer):
    """Revision model serializer."""
    order = OrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Revision
        fields = (
            "id",
            "order",
            "reason",
        )

    def create(self, validated_data):
        request = self.context['request']
        order = self.context['order']
        validated_data['order'] = order
        revision = Revision.objects.create(**validated_data)
        activity = Activity.objects.create(
            type=Activity.REVISION,
            order=order
        )
        RevisionActivity.objects.create(
            activity=activity,
            revision=revision
        )

        issued_by = order.seller
        issued_to = order.buyer

        chats = Chat.objects.filter(participants=issued_by)
        chats = chats.filter(participants=issued_to)

        chat_instance = None
        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    chat_instance = chat

        if not chat_instance:

            chat_instance = Chat.objects.create()

            chat_instance.participants.add(issued_to)
            chat_instance.participants.add(issued_by)
            chat_instance.save()

        # Create the message

        message = Message.objects.create(chat=chat_instance, activity=activity, sent_by=issued_by)
        chat_instance.last_message = message
        chat_instance.save()
        # Set message seen
        seen_by, created = SeenBy.objects.get_or_create(chat=chat_instance, user=issued_by)
        if seen_by.message != chat_instance.last_message:

            seen_by.message = chat_instance.last_message
            seen_by.save()
        return revision
