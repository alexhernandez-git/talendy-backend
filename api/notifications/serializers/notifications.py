"""Notifications serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer, ConnectionModelSerializer, ReviewModelSerializer
from api.chats.serializers import MessageModelSerializer
from api.posts.serializers import ContributeRequestModelSerializer, PostModelSerializer, PostMessageModelSerializer
from api.donations.serializers import DonationModelSerializer

# Models
from api.users.models import User
from api.notifications.models import NotificationUser, Notification


class NotificationModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    actor = UserModelSerializer(read_only=True)
    messages = serializers.SerializerMethodField(read_only=True)
    connection = serializers.SerializerMethodField(read_only=True)
    contribute_request = serializers.SerializerMethodField(read_only=True)
    post = serializers.SerializerMethodField(read_only=True)
    member_joined = serializers.SerializerMethodField(read_only=True)
    post_messages = serializers.SerializerMethodField(read_only=True)
    review = serializers.SerializerMethodField(read_only=True)
    donation = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Notification
        fields = (
            "id",
            "type",
            "actor",
            "messages",
            "connection",
            "post",
            "member_joined",
            "post_messages",
            "contribute_request",
            "review",
            "donation",
            "modified",
        )

        read_only_fields = ("id",)

    def get_messages(self, obj):
        return MessageModelSerializer(obj.messages, many=True).data

    def get_post_messages(self, obj):
        return PostMessageModelSerializer(obj.post_messages, many=True).data

    def get_connection(self, obj):
        if obj.connection:
            return ConnectionModelSerializer(obj.connection, many=False).data
        return False

    def get_contribute_request(self, obj):
        if obj.contribute_request:
            return ContributeRequestModelSerializer(obj.contribute_request, many=False).data
        return False

    def get_post(self, obj):
        if obj.post:
            return PostModelSerializer(obj.post, many=False).data
        return False

    def get_member_joined(self, obj):
        if obj.member_joined:
            return UserModelSerializer(obj.member_joined, many=False).data
        return False

    def get_review(self, obj):
        if obj.review:
            return ReviewModelSerializer(obj.review, many=False).data
        return False

    def get_donation(self, obj):
        if obj.donation:
            return DonationModelSerializer(obj.donation, many=False).data
        return False


class NotificationUserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    user = UserModelSerializer(read_only=True)
    notification = NotificationModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = NotificationUser
        fields = (
            "id",
            "user",
            "notification",
            "is_read",
        )

        read_only_fields = ("id",)


class ReadNotificationSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        instance.is_read = True
        instance.save()

        return instance
