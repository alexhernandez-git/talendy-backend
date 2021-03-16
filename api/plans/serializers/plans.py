"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from api.plans.models import Plan


class PlanModelSerializer(serializers.ModelSerializer):
    """Plan model serializer."""

    class Meta:
        """Meta class."""

        model = Plan
        fields = (
            "id",
            "type",
            "unit_amount",
            "currency",
            "price_label"
        )

        read_only_fields = ("id",)
