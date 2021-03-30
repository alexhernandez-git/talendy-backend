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

# Serializers
from api.users.serializers import UserModelSerializer

# Utils
from datetime import timedelta
import re
from django.utils import timezone


class OfferModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""
    seller = UserModelSerializer(read_only=True)
    buyer = UserModelSerializer(read_only=True)

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
        from api.utils.helpers import convert_currency
        request = self.context['request']
        user = request.user
        if user.karmas_amount < data['karmas_amount']:
            raise serializers.ValidationError(
                "You have not enough karmas")
        return super().validate(data)

    def create(self, validated_data):
        from api.taskapp.tasks import send_offer_to_followers

        request = self.context['request']

        # Create the offer

        buyer = request.user
        buyer.karmas_amount -= validated_data['karmas_amount']
        validated_data['buyer'] = buyer

        offer = Offer.objects.create(**validated_data)
        send
        # Send the offer to all follewers

        return offer
