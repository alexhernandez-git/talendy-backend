"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer

# Models
from api.users.models import Rating, User


class RatingModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    followed_user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Rating
        fields = (
            "id",
            "followed_user",
        )

        read_only_fields = ("id",)
