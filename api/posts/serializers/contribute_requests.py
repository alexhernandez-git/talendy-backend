"""Notifications serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer
from api.chats.serializers import MessageModelSerializer

# Models
from api.users.models import User
from api.posts.models import ContributeRequest, Post


class ContributeRequestModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = ContributeRequest
        fields = (
            "id",
            "user",
            "created"
        )

        read_only_fields = ("id",)


class RequestContributeSerializer(serializers.Serializer):
    post = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        post = User.objects.get(id=data["post"])

        # Check if is not already follow
        if Post.objects.filter(id=post.id, members=user).exists():
            raise serializers.ValidationError("You already are a member of this post")
        if ContributeRequest.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("This contribute request has already been issued")
        return {"user": user, "post": post}

    def create(self, validated_data):
        user = validated_data["user"]
        post = validated_data["post"]
        contribute_request = ContributeRequest.objects.create(user=user, post=post)
        return contribute_request
