"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from api.donations.models import DonationOption


class DonationOptionModelSerializer(serializers.ModelSerializer):
    """DonationOption model serializer."""

    class Meta:
        """Meta class."""

        model = DonationOption
        fields = (
            "id",
            "type",
            "unit_amount",
            "currency",
            "price_label",
            "paid_karma"
        )

        read_only_fields = ("id",)
