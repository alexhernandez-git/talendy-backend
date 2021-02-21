"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import CancelOrder, Order
from api.activities.models import Activity, CancelOrderActivity
from api.users.models import User
from api.chats.models import Message, Chat, SeenBy

# Serializers
from api.orders.serializers import OrderModelSerializer
from api.users.serializers import UserModelSerializer


class CancelOrderModelSerializer(serializers.ModelSerializer):
    """CancelOrder model serializer."""
    order = OrderModelSerializer(read_only=True)
    issued_by = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = CancelOrder
        fields = (
            "id",
            "order",
            "issued_by",
            "reason",
            "accepted",
            "cancelled"
        )
        extra_kwargs = {"accepted": {"required": False, "allow_null": True},
                        "cancelled": {"required": False, "allow_null": True}}

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        validated_data['issued_by'] = user
        order = self.context['order']
        validated_data['order'] = order
        cancel_order = CancelOrder.objects.create(**validated_data)
        activity = Activity.objects.create(
            type=Activity.CANCEL,
            order=order
        )
        CancelOrderActivity.objects.create(
            activity=activity,
            cancel_order=cancel_order
        )

        seller = order.seller
        buyer = order.buyer

        issued_by = user
        issued_to = None
        if issued_by == seller:
            issued_to = buyer
        else:
            issued_to = seller

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
        return cancel_order
