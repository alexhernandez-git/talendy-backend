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
from .post_members import PostMemberModelSerializer

# Models
from api.users.models import User
from api.posts.models import Post, PostImage, PostMember, ContributeRequest, PostSeenBy
from api.notifications.models import Notification, NotificationUser

# Utils
import json


class PostImageModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PostImage
        fields = (
            "id",
            "image",
            "name",
        )

        read_only_fields = ("id",)


class PostModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    user = UserModelSerializer(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)
    is_contribute_requested = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Post
        fields = (
            "id",
            "user",
            "title",
            "text",
            "community",
            "members",
            "members_count",
            "privacity",
            "status",
            "images",
            "karma_offered",
            "created",
            "solution",
            "is_contribute_requested",
        )

        read_only_fields = ("id", "created")

    def get_images(self, obj):
        return PostImageModelSerializer(PostImage.objects.filter(post=obj.id), many=True).data

    def get_members(self, obj):
        members = PostMember.objects.filter(post=obj.id)
        return PostMemberModelSerializer(members, many=True).data

    def get_is_contribute_requested(self, obj):
        if 'request' in self.context:
            request = self.context['request']
            if request.user.id:
                user = request.user
                return ContributeRequest.objects.filter(post=obj.id, user=user).exists()
        return False

    def validate(self, data):
        user = self.context['request'].user
        if 'karma_offered' in data and int(data['karma_offered']) < 100:
            raise serializers.ValidationError("Not enough karma offered")
        if 'karma_offered' in data and int(data['karma_offered']) > user.karma_amount:
            raise serializers.ValidationError("You don't have enough karma")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        images = self.context["images"]
        post = Post.objects.create(user=user, **validated_data, members_count=1)

        user.karma_amount = user.karma_amount - post.karma_offered
        user.posts_count += 1
        user.created_posts_count += 1
        user.created_active_posts_count += 1
        user.save()
        for image in images:

            PostImage.objects.create(
                post=post,
                name=image.name,
                image=image,
                size=image.size
            )
        PostMember.objects.create(post=post, user=user, role=PostMember.ADMIN)
        return post

    def update(self, instance, validated_data):
        validated_data.pop("karma_offered", None)
        images = self.context["images"]
        current_images = json.loads(self.context["current_images"])

        PostImage.objects.filter(post=instance).exclude(pk__in=current_images).delete()
        for image in images:
            PostImage.objects.create(
                post=instance,
                name=image.name,
                image=image,
                size=image.size
            )
        return super(PostModelSerializer, self).update(instance, validated_data)


class RetrieveContributeRoomModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    user = UserModelSerializer(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)
    is_last_message_seen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Post
        fields = (
            "id",
            "is_last_message_seen",
            "user",
            "title",
            "text",
            "community",
            "members",
            "members_count",
            "shared_notes",
            "privacity",
            "status",
            "images",
            "karma_offered",
            "solution",
            "created",
        )

        read_only_fields = ("id",)

    def get_images(self, obj):
        return PostImageModelSerializer(PostImage.objects.filter(post=obj.id), many=True).data

    def get_members(self, obj):
        members = PostMember.objects.filter(post=obj.id)
        return PostMemberModelSerializer(members, many=True).data

    def get_is_last_message_seen(self, obj):
        user = self.context["request"].user
        return NotificationUser.objects.filter(
            notification__post=obj, notification__type=Notification.POST_MESSAGES, is_read=False,
            user=user).exists()


class ClearPostChatNotificationSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        user = self.context['request'].user
        notifications = NotificationUser.objects.filter(
            notification__post=instance, notification__type=Notification.POST_MESSAGES, is_read=False, user=user)

        for notification in notifications:
            notification.is_read = True
            notification.save()

        user.save()

        return instance


class UpdatePostSharedNotesSerializer(serializers.Serializer):
    shared_notes = serializers.CharField()

    def update(self, instance, validated_data):
        instance.shared_notes = validated_data['shared_notes']
        instance.save()

        return instance


class UpdatePostSolutionSerializer(serializers.Serializer):
    solution = serializers.CharField()

    def update(self, instance, validated_data):
        instance.solution = validated_data['solution']
        instance.save()

        return instance
