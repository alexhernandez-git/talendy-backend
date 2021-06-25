
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404


# Models
from api.portals.models import PlanPayment


class PlanPaymentModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PlanPayment
        fields = (
            "id",
            "invoice_id",
            "charge_id",
            "subscription_id",
            "amount_paid",
            "currency",
            "paid",
            "status",
            "invoice_pdf",
            "created"
        )

        read_only_fields = ("id",)
