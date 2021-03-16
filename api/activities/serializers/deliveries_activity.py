# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import OfferActivity

# Serializers
from api.orders.serializers import DeliveryModelSerializer


class DeliveryActivityModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""
    delivery = DeliveryModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = OfferActivity
        fields = (
            "id",
            "delivery",
            "status"
        )

        read_only_fields = ("id",)
