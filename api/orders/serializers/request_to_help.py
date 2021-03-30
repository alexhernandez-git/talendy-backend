"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Offer, Order
from api.activities.models import Activity, RequestToHelpActivity
from api.users.models import User
from api.chats.models import Message, Chat, SeenBy

# Serializers
from api.users.serializers import UserModelSerializer
from api.orders.serializers import OfferModelSerializer

# Utils
from datetime import timedelta
import re
from django.utils import timezone


class OfferModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""
    seller = UserModelSerializer(read_only=True)
    offer = OfferModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Offer
        fields = (
            "id",
            "offer",
            "seller",
            "text",
            "accepted"
        )
        read_only_fields = ("id",)

    def validate(self, data):
        offer = get_object_or_404(Offer, id=self.context['offer'])

        orders = Order.objects.filter(offer=offer.id, status=Order.ACTIVE)

        if orders.exists():
            raise serializers.ValidationError(
                "There is already someone doing this task")

    def create(self, validated_data):
        from api.taskapp.tasks import send_request_to_help
        request = self.context['request']
        offer = get_object_or_404(Offer, id=self.context['offer'])

        # Get the seller
        seller = request.user
        validated_data['seller'] = seller

        # Get the amount at delivery
        delivery_time = validated_data['delivery_time']
        if delivery_time:
            now = timezone.now()
            # Get delivery date
            delivery_date = now + timedelta(days=delivery_time)
            validated_data['delivery_date'] = delivery_date

        try:
            buyer = User.objects.get(pk=self.context['buyer'])
            validated_data['buyer'] = buyer

        except:
            buyer = None

        request_to_help = Offer.objects.create(**validated_data)

        # Create the actions
        activity = Activity.objects.create(
            type=Activity.REQUEST_TO_HELP,
        )
        RequestToHelpActivity.objects.create(
            activity=activity,
            request_to_help=request_to_help
        )

        buyer_email = None
        # Get the buyer

        user_exists = True

        # Check if user exists

        send_request_to_help(seller, buyer.email, True, offer.id, buyer.id)

        # Get or create the chat

        chats = Chat.objects.filter(participants=seller)
        chats = chats.filter(participants=buyer)
        chat_instance = None
        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    chat_instance = chat

        if not chat_instance:

            chat_instance = Chat.objects.create()

            chat_instance.participants.add(buyer)
            chat_instance.participants.add(seller)
            chat_instance.save()

        # Create the message

        message = Message.objects.create(chat=chat_instance, activity=activity, sent_by=seller)
        chat_instance.last_message = message
        chat_instance.save()

        # Set message seen
        seen_by, created = SeenBy.objects.get_or_create(chat=chat_instance, user=seller)
        if seen_by.message != chat_instance.last_message:

            seen_by.message = chat_instance.last_message
            seen_by.save()

        return offer
