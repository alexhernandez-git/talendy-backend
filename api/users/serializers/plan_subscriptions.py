
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404


# Models
from api.users.models import PlanSubscription, User


class PlanSubscriptionModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PlanSubscription
        fields = (
            "id",
            "subscription_id",
            "product_id",
            "to_be_cancelled",
            "cancelled",
            "status",
            "payment_issue",
            "current_period_end",
            "plan_type",
            "plan_unit_amount",
            "plan_currency",
            "plan_price_label"
        )

        read_only_fields = ("id",)
