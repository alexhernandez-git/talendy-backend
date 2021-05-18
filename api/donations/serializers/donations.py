
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from djmoney.models.fields import Money

# Models
from api.donations.models import Donation, DonationOption, DonationPayment
from api.users.models import User, Earning

# Serializers
from api.users.serializers import UserModelSerializer
from .donation_payments import DonationPaymentModelSerializer
from .donation_options import DonationOptionModelSerializer

# Utils
import string
import random
from api.utils import helpers
from datetime import timedelta
from django.utils import timezone


class DonationModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    from_user = UserModelSerializer(read_only=True)
    donation_option = DonationOptionModelSerializer(required=False)
    donation_payment = DonationPaymentModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Donation
        fields = (
            "id",
            "is_other_amount",
            "donation_option",
            "donation_payment",
            "from_user",
            "net_amount",
            "is_anonymous",
            "message",
            "email",
            "created"
        )

        read_only_fields = ("id", "net_amount")
