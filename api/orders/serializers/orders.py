"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Order


class OrderModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Order
        fields = (
            "id",
            "buyer",
            "seller",
            "title",
            "description",
            "total_amount",
            "is_split_payment",
            "first_payment",
            "amount_at_delivery",
            "delivery_date",
            "order_time",
            "status"
        )

        read_only_fields = ("id",)
