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
from api.posts.models import CollaborateRequest, Post
from api.notifications.models import Notification, NotificationUser

# Celery
from api.taskapp.tasks import send_collaborate_request, send_collaborate_request_accepted


class CollaborateRequestModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    user = UserModelSerializer(read_only=True)
    post = PostModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = CollaborateRequest
        fields = (
            "id",
            "user",
            "post",
            "reason",
            "created"
        )

        read_only_fields = ("id",)


class RequestCollaborateSerializer(serializers.Serializer):
    post = serializers.UUIDField()
    reason = serializers.CharField(max_length=300)

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        post = Post.objects.get(id=data["post"])

        # Check if is not already follow
        if Post.objects.filter(id=post.id, members=user).exists():
            raise serializers.ValidationError("You already are a member of this post")
        if CollaborateRequest.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("This collaborate request has already been issued")
        if post.members_count == 10:
            raise serializers.ValidationError("This post can't be more than 10 members")

        return {"user": user, "post": post, "reason": data['reason']}

    def create(self, validated_data):
        user = validated_data["user"]
        post = validated_data["post"]
        reason = validated_data["reason"]
        collaborate_request = CollaborateRequest.objects.create(user=user, post=post, reason=reason)
        # Notificate the invitation to the addressee
        notification = Notification.objects.create(
            type=Notification.NEW_COLLABORATE_REQUEST,
            collaborate_request=collaborate_request,
        )
        user_notification = NotificationUser.objects.create(
            notification=notification,
            user=post.user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % post.user.id, {
                "type": "send.notification",
                "event": "NEW_COLLABORATE_REQUEST",
                "notification__pk": str(user_notification.pk),
                "collaborate_request__pk": str(collaborate_request.pk),
            }
        )
        if post.user.email_notifications_allowed:
            send_collaborate_request(user, post.user)

        return collaborate_request


class AcceptCollaborateRequestSerializer(serializers.Serializer):
    """User model serializer."""

    def validate(self, data):
        collaborate_request = self.instance
        post = collaborate_request.post
        if post.members_count == 10:
            raise serializers.ValidationError("This post can't be more than 10 members")

        return data

    def update(self, instance, validated_data):
        collaborate_request = instance
        post = collaborate_request.post
        requester_user = collaborate_request.user

        # Add the member
        post.members.add(requester_user)
        post.members_count += 1
        post.save()

        requester_user.posts_count += 1
        requester_user.collaborated_posts_count += 1
        requester_user.collaborated_active_posts_count += 1
        requester_user.save()

        # Remove the collaborate request
        CollaborateRequest.objects.filter(id=collaborate_request.id).delete()

        # Notificate the user is joining to the post

        notification = Notification.objects.create(
            type=Notification.JOINED_MEMBERSHIP,
            post=post,
            member_joined=requester_user
        )

        user_notification = NotificationUser.objects.create(
            notification=notification,
            user=post.user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % post.user.id, {
                "type": "send.notification",
                "event": "JOINED_MEMBERSHIP",
                "notification__pk": str(user_notification.pk),
            }
        )

        notification = Notification.objects.create(
            type=Notification.COLLABORATE_REQUEST_ACCEPTED,
            post=post,
            member_joined=requester_user
        )

        user_notification = NotificationUser.objects.create(
            notification=notification,
            user=requester_user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % requester_user.id, {
                "type": "send.notification",
                "event": "COLLABORATE_REQUEST_ACCEPTED",
                "notification__pk": str(user_notification.pk),
            }
        )
        if requester_user.email_notifications_allowed:
            send_collaborate_request_accepted(post.user, requester_user)
        return instance
