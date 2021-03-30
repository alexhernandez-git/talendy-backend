# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import CancelOrderActivity

# Serializers
from api.orders.serializers import CancelOrderModelSerializer


class CancelOrderActivityModelSerializer(serializers.ModelSerializer):
    """Oportunity model serializer."""
    cancel_order = CancelOrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = CancelOrderActivity
        fields = (
            "id",
            "cancel_order",
            "status"
        )

        read_only_fields = ("id",)
