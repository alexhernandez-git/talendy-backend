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
from api.users.models import Follow, User


class FollowModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    follow_user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Follow
        fields = (
            "id",
            "follow_user",
        )

        read_only_fields = ("id",)


class CreateFollowSerializer(serializers.Serializer):
    """User model serializer."""

    follow_user_id = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        from_user = request.user
        follow_user = User.objects.get(id=data["follow_user_id"])

        # Check if is not already follow
        if from_user == follow_user:
            raise serializers.ValidationError("You can not be your follow")
        if Follow.objects.filter(from_user=from_user, follow_user=follow_user).exists():
            raise serializers.ValidationError("This user is already in your follows")
        return {"from_user": from_user, "follow_user": follow_user}

    def create(self, validated_data):
        from_user = validated_data["from_user"]
        follow_user = validated_data["follow_user"]
        follow = Follow.objects.create(from_user=from_user, follow_user=follow_user)
        return follow
