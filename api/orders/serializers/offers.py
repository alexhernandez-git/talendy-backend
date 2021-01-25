"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Offer
from api.activities.models import Activity, OfferActivity
from api.users.models import User
from api.chats.models import Message, Chat


# Utils
from datetime import datetime, timedelta
from djmoney.money import Money
from forex_python.converter import CurrencyRates
from api.taskapp.tasks import send_offer


class OfferModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""

    class Meta:
        """Meta class."""

        model = Offer
        fields = (
            "id",
            "buyer",
            "seller",
            "title",
            "description",
            "total_amount",
            "two_payments_order",
            "first_payment",
            "amount_at_delivery",
            "delivery_date",
            "days_for_delivery",
            "accepted"
        )

        optional_fields = ["first_payment", ]
        read_only_fields = ("id", "seller", "amount_at_delivery", "delivery_date", "accepted")
        extra_kwargs = {"first_payment": {"required": False, "allow_null": True},
                        "buyer": {"required": False, "allow_null": True}}

    def validate(self, data):
        c = CurrencyRates()
        request = self.context['request']
        user = request.user
        total_amount = data["total_amount"]
        if data['two_payments_order']:
            first_payment = data["first_payment"]
            if total_amount < first_payment:
                raise serializers.ValidationError("First payment can't be greater than total amount")
            converted_first_payment = c.convert(user.currency, 'USD', first_payment)
            data["first_payment"] = converted_first_payment
        converted_total_amount = c.convert(user.currency, 'USD', total_amount)
        data["total_amount"] = converted_total_amount

        return super().validate(data)

    def create(self, validated_data):
        request = self.context['request']
        send_offer_by_email = self.context['send_offer_by_email']

        # Create the offer

        # Get the seller
        seller = request.user
        validated_data['seller'] = seller

        # Get the amount at delivery
        days_for_delivery = validated_data['days_for_delivery']
        now = datetime.now()
        # Get delivery date
        delivery_date = now + timedelta(days=days_for_delivery)
        validated_data['delivery_date'] = delivery_date

        offer = Offer.objects.create(**validated_data)

        # Create the actions
        activity = Activity.objects.create(
            type=Activity.OFFER,
        )
        OfferActivity.objects.create(
            activity=activity,
            offer=offer
        )

        buyer = validated_data['buyer']
        buyer_email = None
        # Get the buyer
        if send_offer_by_email:
            buyer_email = self.context["buyer_email"]
            send_offer(seller, buyer_email, True)
        else:
            send_offer(seller, buyer.email, False)

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

            Message.objects.create(chat=chat_instance, activity=activity, sent_by=seller)

        return offer
