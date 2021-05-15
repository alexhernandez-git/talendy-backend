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
from api.posts.serializers import PostModelSerializer

# Models
from api.users.models import Review, User


class ReviewModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    review_user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Review
        fields = (
            "id",
            "rating",
            "comment",
            "from_post",
            "review_user",
            "created"
        )

        read_only_fields = ("id",)
