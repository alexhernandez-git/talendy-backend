"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Delivery, Order
from api.activities.models import Activity, DeliveryActivity
from api.users.models import User
from api.chats.models import Message, Chat, SeenBy

# Serializers
from api.orders.serializers import OrderModelSerializer


class DeliveryModelSerializer(serializers.ModelSerializer):
    """Delivery model serializer."""
    order = OrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Delivery
        fields = (
            "id",
            "order",
            "response",
            "source_file"
        )
        extra_kwargs = {"source_file": {"required": False, "allow_null": True}}

    def validate(self, data):
        order = self.context['order']
        request = self.context['request']
        user = request.user
        if user != order.seller:
            raise serializers.ValidationError('You are not allowed to do this action')
        if order.status == Order.DELIVERED:
            raise serializers.ValidationError('This order is already delivered')
        if order.status == Order.CANCELLED:
            raise serializers.ValidationError('This order is cancelled')
        return data

    def create(self, validated_data):

        order = self.context['order']
        validated_data['order'] = order
        delivery = Delivery.objects.create(**validated_data)
        activity = Activity.objects.create(
            type=Activity.DELIVERY,
            order=order
        )
        DeliveryActivity.objects.create(
            activity=activity,
            delivery=delivery
        )

        seller = order.seller
        buyer = order.buyer

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

        return delivery


class AcceptDeliveryModelSerializer(serializers.ModelSerializer):
    """Delivery model serializer."""
    order = OrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Delivery
        fields = (
            "id",
            "order",
            "response",
            "source_file"
        )
        read_only_fields = (
            "id",
            "order",
            "response",
            "source_file"
        )
        extra_kwargs = {"source_file": {"required": False, "allow_null": True}}

    def validate(self, data):
        delivery = self.instance
        order = delivery.order
        request = self.context['request']
        user = request.user
        if user != order.buyer:
            raise serializers.ValidationError('You are not allowed to do this action')
        if order.status == Order.DELIVERED:
            raise serializers.ValidationError('This order is already delivered')
        if order.status == Order.CANCELLED:
            raise serializers.ValidationError('This order is cancelled')

        return data

    def update(self, instance,  validated_data):
        order = instance.order

        activity = Activity.objects.create(
            type=Activity.DELIVERY,
            order=order
        )
        DeliveryActivity.objects.create(
            activity=activity,
            delivery=instance,
            status=DeliveryActivity.ACCEPTED
        )

        issued_to = order.seller
        issued_by = order.buyer

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

        order.status = Order.DELIVERED
        if order.type == Order.NORMAL_ORDER:
            # Return de money to user as credits
            seller = order.seller
            seller.net_income = seller.net_income + order.due_to_seller
            seller.available_for_withdawal = seller.available_for_withdawal + order.due_to_seller
            seller.save()
        order.save()

        return instance
