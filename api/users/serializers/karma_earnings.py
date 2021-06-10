
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.db.models import Sum

# Models
from api.users.models import KarmaEarning, User


class KarmaEarningModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = KarmaEarning
        fields = (
            "id",
            "type",
            "amount",
            "created",
        )

        read_only_fields = ("id",)
