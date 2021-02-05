"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Offer, Order
from api.activities.models import Activity, OfferActivity
from api.users.models import User
from api.chats.models import Message, Chat, SeenBy


# Utils
from datetime import datetime, timedelta
from djmoney.money import Money
from api.taskapp import tasks
import re
from api.utils import helpers


class OfferModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""

    class Meta:
        """Meta class."""

        model = Offer
        fields = (
            "id",
            "send_offer_by_email",
            "buyer_email",
            "buyer",
            "seller",
            "title",
            "description",
            "unit_amount",
            "type",
            "first_payment",
            "payment_at_delivery",
            "delivery_date",
            "delivery_time",
            "accepted",
            "interval_subscription",
            "rate_date"

        )

        read_only_fields = ("id", "seller", "delivery_date", "accepted")
        extra_kwargs = {"first_payment": {"required": False, "allow_null": True},
                        "buyer": {"required": False, "allow_null": True},
                        "buyer_email": {"required": False, "allow_null": True},
                        "interval_subscription": {"required": False, "allow_null": True},
                        "rate_date": {"required": False, "allow_null": True},
                        }

    def validate(self, data):

        request = self.context['request']
        user = request.user
        unit_amount = data["unit_amount"]
        rate_date = None
        # If the offer is by email check if the buyer email is correct
        if data["send_offer_by_email"]:
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if not re.search(regex,  data["buyer_email"]):
                raise serializers.ValidationError("The buyer email address is not correct")

        converted_unit_amount, rate_date = helpers.convert_currency('USD', user.currency, unit_amount)
        data["unit_amount"] = converted_unit_amount
        if data['type'] == Order.TWO_PAYMENTS_ORDER:
            first_payment = data["first_payment"]
            if unit_amount < first_payment:
                raise serializers.ValidationError("First payment can't be greater than total amount")
            converted_first_payment, rate_date = helpers.convert_currency('USD', user.currency, first_payment)

            data["first_payment"] = converted_first_payment
            data["payment_at_delivery"] = converted_unit_amount - converted_first_payment
        data['rate_date'] = rate_date
        return super().validate(data)

    def create(self, validated_data):
        request = self.context['request']
        send_offer_by_email = validated_data['send_offer_by_email']

        # Create the offer

        # Get the seller
        seller = request.user
        validated_data['seller'] = seller

        # Get the amount at delivery
        delivery_time = validated_data['delivery_time']
        if delivery_time:
            now = datetime.now()
            # Get delivery date
            delivery_date = now + timedelta(days=delivery_time)
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

        user_exists = True

        # Check if user exists

        if send_offer_by_email:
            buyer_email = validated_data["buyer_email"]
            users_queryset = None
            users_queryset = User.objects.filter(email=buyer_email)
            if users_queryset.exists():
                user_exists = True
                buyer = users_queryset.first()
                validated_data['buyer'] = buyer
                validated_data['send_offer_by_email'] = False
            else:
                user_exists = False

        if not user_exists:
            tasks.send_offer(seller, buyer_email, user_exists, offer.id)

        else:
            tasks.send_offer(seller, buyer.email, True, offer.id, buyer.id)

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
