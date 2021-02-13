# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import MoneyReceivedActivity

# Serializers
from api.orders.serializers import OrderModelSerializer


class MoneyReceivedActivityModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""
    order = OrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = MoneyReceivedActivity
        fields = (
            "id",
            "order",
            "amount"
        )

        read_only_fields = ("id",)
