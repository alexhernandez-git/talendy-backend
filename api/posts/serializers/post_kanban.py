"""Notifications serializers."""

# Django REST Framework
from api.taskapp.tasks import send_post_finalized, send_post_to_followers
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Sum, Q

# Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Serializers
from api.users.serializers import UserModelSerializer
from .post_members import PostMemberModelSerializer

# Models
from api.users.models import User, Review, Follow, Connection
from api.posts.models import Post, KanbanCard, KanbanList, PostMember, CollaborateRequest, PostSeenBy
from api.notifications.models import Notification, NotificationUser

# Utils
import json


class KanbanCardModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = KanbanCard
        fields = (
            "id",
            "title",
        )


class KanbanListModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    cards = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = KanbanList
        fields = (
            "id",
            "title",
            "cards",
        )

        read_only_fields = ("id", "created")

    def get_images(self, obj):
        return KanbanCardModelSerializer(KanbanCard.objects.filter(list=obj.id), many=True).data

    def validate(self, data):
        user = self.context['request'].user
        post = self.context['post']

        if not post.members.filter(user=user).exists():
            raise serializers.ValidationError("Not enough karma offered")

        return data

    def create(self, validated_data):

        post = self.context['post']
        title = validated_data["title"]
        # Get the kanban list higher order number
        order = 0
        if KanbanList.objects.filter(post=post).order_by("-order").exists():
            last_kanban_list = KanbanList.objects.filter(post=post).order_by("-order").exists()
            order = ++last_kanban_list.order
        list = KanbanList.objects.create(title=title, post=post, order=order)

        return list


class RetrieveCollaborateRoomModelSerializer(serializers.ModelSerializer):
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
            "draft_solution",
            "karma_winner",
            "created",
        )

        read_only_fields = ("id",)

    def get_images(self, obj):
        return PostImageModelSerializer(PostImage.objects.filter(post=obj.id), many=True).data

    def get_members(self, obj):
        members = PostMember.objects.filter(post=obj.id)
        return PostMemberModelSerializer(members, many=True).data

    def get_is_last_message_seen(self, obj):
        if "request" in self.context and self.context["request"].user.id:

            user = self.context["request"].user
            return NotificationUser.objects.filter(
                notification__post=obj, notification__type=Notification.POST_MESSAGES, is_read=False,
                user=user).exists()
        return None


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
    solution = serializers.CharField(allow_blank=True)

    def update(self, instance, validated_data):
        instance.draft_solution = validated_data['solution']
        instance.save()

        return instance


class UpdatePostWinnerKarmaSerializer(serializers.Serializer):
    karma_winner = serializers.UUIDField()

    def validate(self, data):
        # Validate if the memeber exists
        karma_winner = get_object_or_404(PostMember, id=data.get('karma_winner'))
        return {"karma_winner": karma_winner}

    def update(self, instance, validated_data):
        instance.karma_winner = validated_data.get('karma_winner')
        instance.save()

        return instance


class FinalizePostSerializer(serializers.Serializer):

    def validate(self, data):
        post = self.instance
        if post.members.all().count() > 1 and not post.karma_winner:
            raise serializers.ValidationError("You need a karma winner")

        return data

    def update(self, instance, validated_data):
        post = instance
        admin = post.user

        # Save the draft_solution to post
        post.solution = post.draft_solution

        # Substract admin created_active_posts_count
        admin.created_active_posts_count -= 1

        # Add admin created_solved_posts_count
        admin.created_solved_posts_count += 1

        # Give the karma to the winner
        if post.karma_winner:
            karma_winner = post.karma_winner.user
            karma_winner.karma_amount += post.karma_offered
            karma_winner.save()

        # Update the post finalized to members
        members = PostMember.objects.filter(post=post).exclude(user=admin)
        for member in members:
            user = member.user
            # Substract user collaborated_active_posts_count
            user.collaborated_active_posts_count -= 1
            # Add user collaborated_solved_posts_count
            user.collaborated_solved_posts_count += 1

            # Check if there is a review
            if (member.draft_rating and member.draft_rating > 0) or member.draft_comment:
                # Save the review to the user
                review = Review.objects.create(
                    review_user=admin,
                    reviewd_user=user,
                    from_post=post,
                    rating=member.draft_rating,
                    comment=member.draft_comment,
                )
                user.reviews_count += 1
                notification = Notification.objects.create(
                    type=Notification.NEW_REVIEW,
                    review=review,
                )
                user_notification = NotificationUser.objects.create(
                    notification=notification,
                    user=user
                )

            # Update the user review avg
            user_avg = Review.objects.filter(
                reviewd_user=user
            ).exclude(rating=None).aggregate(Avg('rating'))['rating__avg']

            user.reputation = user_avg
            notification = Notification.objects.create(
                type=Notification.POST_FINALIZED,
                post=post,
            )
            user_notification = NotificationUser.objects.create(
                notification=notification,
                user=user
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "user-%s" % user.id, {
                    "type": "send.notification",
                    "event": "POST_FINALIZED",
                    "notification__pk": str(user_notification.pk),
                }
            )
            if not user.is_online and user.email_notifications_allowed:
                send_post_finalized(admin, user, post)
            user.save()

        admin.save()
        post.status = Post.SOLVED
        post.save()
        return instance


class StopCollaboratingSerializer(serializers.Serializer):

    def validate(self, data):
        user = self.context['request'].user
        post = self.instance
        # Validate is not owner
        if post.user.id == user.id:
            raise serializers.ValidationError("You are the owner")

        # Validate post is not finished
        if post.status == Post.SOLVED:
            raise serializers.ValidationError("This post is finished")

        # Validate if you are member if this post
        if not post.members.filter(id=user.id).exists():
            raise serializers.ValidationError("You are not member of this post")
        return data

    def update(self, instance, validated_data):
        user = self.context['request'].user

        post = instance
        # Remove member to post
        post.members.remove(user)
        post.members_count -= 1
        post.save()

        # Substract the post from user
        user.posts_count -= 1
        user.collaborated_posts_count -= 1
        user.collaborated_active_posts_count -= 1
        user.save()
        return instance
