"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Order
from api.users.models import User, Earning
from api.activities.models import Activity, RequestToHelpActivity
from api.orders.models import Offer, RequestToHelp
from api.chats.models import Message, Chat, SeenBy
from djmoney.models.fields import Money

# Serializers
from api.users.serializers import UserModelSerializer

# Utils
from api.utils import helpers
from datetime import timedelta
from django.utils import timezone


class OrderModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    seller = UserModelSerializer()
    buyer = UserModelSerializer()

    class Meta:
        """Meta class."""

        model = Order
        fields = (
            "__all__")

        read_only_fields = ("id",)


class AcceptOrderSerializer(serializers.Serializer):
    """Acount verification serializer."""
    payment_method_id = serializers.CharField()
    order = OrderModelSerializer(read_only=True)

    def validate(self, data):
        """Update user's verified status."""

        payment_method_id = data['payment_method_id']
        request_to_help = self.context['request_to_help']
        stripe = self.context['stripe']
        request = self.context['request']
        user = request.user

        request_to_help_object = get_object_or_404(RequestToHelp, id=request_to_help['id'])
        self.context['request_to_help_object'] = request_to_help_object

        orders = Order.objects.filter(offer=request_to_help_object.offer.id, status=Order.ACTIVE)

        if orders.exists():
            raise serializers.ValidationError(
                "There is already someone doing this task")

        offer_object = get_object_or_404(Offer, id=request_to_help_object.offer.id)
        self.context['offer_object'] = offer_object

        return data

    def create(self, validated_data):

        offer_object = self.context['offer_object']
        request_to_help_object = self.context['request_to_help_object']

        new_order = Order.objects.create(
            offer=offer_object,
            buyer=offer_object.buyer,
            seller=offer_object.seller,
            karmas_amount=offer_object.karmas_amount,
        )

        request_to_help_queryset = RequestToHelpActivity.objects.filter(
            request_to_help=request_to_help_object, status=RequestToHelpActivity.PENDENDT)

        request_to_help = None
        if request_to_help_queryset.exists():
            request_to_help = request_to_help_queryset.first()

        activity = request_to_help.activity
        activity.closed = True
        activity.active = False
        activity = Activity.objects.create(
            type=Activity.REQUEST_TO_HELP,
            order=new_order,
            closed=True,
            active=False
        )
        RequestToHelpActivity.objects.create(
            activity=activity,
            request_to_help=request_to_help_object,
            status=RequestToHelpActivity.ACCEPTED
        )

        chats = Chat.objects.filter(participants=new_order.seller)
        chats = chats.filter(participants=new_order.buyer)
        chat_instance = None
        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    chat_instance = chat

        if not chat_instance:

            chat_instance = Chat.objects.create()

            chat_instance.participants.add(new_order.buyer)
            chat_instance.participants.add(new_order.seller)
            chat_instance.save()

        # Create the message

        message = Message.objects.create(chat=chat_instance, activity=activity, sent_by=new_order.buyer)
        chat_instance.last_message = message
        chat_instance.save()

        # Set message seen
        seen_by, _ = SeenBy.objects.get_or_create(chat=chat_instance, user=new_order.buyer)
        if seen_by.message != chat_instance.last_message:

            seen_by.message = chat_instance.last_message
            seen_by.save()

        request_to_help_object.accepted = True
        request_to_help_object.save()
        new_order.seller.active_month = True
        new_order.seller.save()
        return new_order
