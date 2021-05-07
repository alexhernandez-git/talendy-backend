"""Notifications serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Serializers
from api.users.serializers import UserModelSerializer
from api.chats.serializers import MessageModelSerializer
from api.posts.serializers import PostModelSerializer

# Models
from api.users.models import User
from api.posts.models import ContributeRequest, Post
from api.notifications.models import Notification, NotificationUser


class ContributeRequestModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    user = UserModelSerializer(read_only=True)
    post = PostModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = ContributeRequest
        fields = (
            "id",
            "user",
            "post",
            "created"
        )

        read_only_fields = ("id",)


class RequestContributeSerializer(serializers.Serializer):
    post = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        post = Post.objects.get(id=data["post"])

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
        # Notificate the invitation to the addressee
        notification = Notification.objects.create(
            type=Notification.NEW_CONTRIBUTE_REQUEST,
            contribute_request=contribute_request,
        )
        user_notification = NotificationUser.objects.create(
            notification=notification,
            user=post.user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % post.user.id, {
                "type": "send.notification",
                "event": "NEW_CONTRIBUTE_REQUEST",
                "notification__pk": str(user_notification.pk),
                "contribute_request__pk": str(contribute_request.pk),
            }
        )
        return contribute_request
