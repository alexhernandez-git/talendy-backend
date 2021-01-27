# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import OfferActivity

# Serializers
from api.orders.serializers import OfferModelSerializer


class OfferActivityModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""
    offer = OfferModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = OfferActivity
        fields = (
            "id",
            "offer",
        )

        read_only_fields = ("id",)
