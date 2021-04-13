"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from api.donations.models import DonationItem


class DonationItemModelSerializer(serializers.ModelSerializer):
    """DonationItem model serializer."""

    class Meta:
        """Meta class."""

        model = DonationItem
        fields = (
            "id",
            "type",
            "unit_amount",
            "currency",
            "price_label"
        )

        read_only_fields = ("id",)
