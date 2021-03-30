"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Oportunity, Order
from api.activities.models import Activity
from api.users.models import User, Follow
from api.chats.models import Message, Chat, SeenBy

# Serializers
from api.users.serializers import UserModelSerializer

# Utils
from datetime import timedelta
import re
from django.utils import timezone


class OportunityModelSerializer(serializers.ModelSerializer):
    """Oportunity model serializer."""
    seller = UserModelSerializer(read_only=True)
    buyer = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Oportunity
        fields = (
            "id",
            "buyer",
            "title",
            "description",
            "karmas_amount",
        )

        read_only_fields = ("id",)

    def validate(self, data):
        from api.utils.helpers import convert_currency
        request = self.context['request']
        user = request.user
        if user.karmas_amount < data['karmas_amount']:
            raise serializers.ValidationError(
                "You have not enough karmas")
        return super().validate(data)

    def create(self, validated_data):
        from api.taskapp.tasks import send_oportunity_to_followers

        request = self.context['request']

        # Create the oportunity

        buyer = request.user
        buyer.karmas_amount -= validated_data['karmas_amount']
        validated_data['buyer'] = buyer

        oportunity = Oportunity.objects.create(**validated_data)

        # Send the oportunity to all follewers
        followers_emails = Follow.objects.filter(follow_user=buyer).values_list('follow_user__email')
        followers_emails_list = [x[0] for x in followers_emails]
        send_oportunity_to_followers(buyer, followers_emails_list, oportunity)

        return oportunity
