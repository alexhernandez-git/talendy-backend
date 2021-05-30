"""Notifications serializers."""

# Django REST Framework
from api.posts.serializers.post_kanbans import KanbanListModelSerializer
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
from api.posts.models import Post, PostImage, PostMember, CollaborateRequest, PostSeenBy, KanbanList, KanbanCard
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
    is_collaborate_requested = serializers.SerializerMethodField(read_only=True)

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
            "is_collaborate_requested",
        )

        read_only_fields = ("id", "created")

    def get_images(self, obj):
        return PostImageModelSerializer(PostImage.objects.filter(post=obj.id), many=True).data

    def get_members(self, obj):
        members = PostMember.objects.filter(post=obj.id)
        return PostMemberModelSerializer(members, many=True).data

    def get_is_collaborate_requested(self, obj):
        if 'request' in self.context:
            request = self.context['request']
            if request.user.id:
                user = request.user
                return CollaborateRequest.objects.filter(post=obj.id, user=user).exists()
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

        users_following = Follow.objects.filter(followed_user=user)
        for user_following in users_following:
            # Create the notification for the user
            if post.privacity == Post.CONNECTIONS_ONLY and not Connection.objects.filter(
                    Q(requester=user, addressee=user_following.from_user) |
                    Q(requester=user_following.from_user, addressee=user),
                    accepted=True).exists():
                break
            notification = Notification.objects.create(
                type=Notification.POST_CREATED_BY_A_USER_FOLLOWED,
                post=post,
            )
            user_notification = NotificationUser.objects.create(
                notification=notification,
                user=user_following.from_user
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "user-%s" % user_following.from_user.id, {
                    "type": "send.notification",
                    "event": "POST_CREATED_BY_A_USER_FOLLOWED",
                    "notification__pk": str(user_notification.pk),
                }
            )

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


class RetrieveCollaborateRoomModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    user = UserModelSerializer(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)
    kanban = serializers.SerializerMethodField(read_only=True)
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
            "kanban",
            "karma_offered",
            "solution",
            "draft_solution",
            "karma_winner",
            "created",
        )

        read_only_fields = ("id",)

    def get_images(self, obj):
        return PostImageModelSerializer(PostImage.objects.filter(post=obj.id), many=True).data

    def get_kanban(self, obj):
        return KanbanListModelSerializer(KanbanList.objects.filter(post=obj.id), many=True).data

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


class UpdateKanbanListOrderSerializer(serializers.Serializer):
    droppable_index_start = serializers.IntegerField()
    droppable_index_end = serializers.IntegerField()

    def update(self, instance, validated_data):
        droppable_index_start = validated_data['droppable_index_start']
        droppable_index_end = validated_data['droppable_index_end']
        kanban_lists = KanbanList.objects.filter(post=instance)
        kanban_list_start = kanban_lists.get(order=droppable_index_start)
        kanban_list_start.order = droppable_index_end

        kanban_list_end = kanban_lists.get(order=droppable_index_end)
        kanban_list_end.order = droppable_index_start

        kanban_list_start.save()
        kanban_list_end.save()

        return instance


class UpdateKanbanCardOrderSerializer(serializers.Serializer):
    list_id = serializers.UUIDField()
    droppable_index_start = serializers.IntegerField()
    droppable_index_end = serializers.IntegerField()

    def update(self, instance, validated_data):
        list_id = validated_data['list_id']
        droppable_index_start = validated_data['droppable_index_start']
        droppable_index_end = validated_data['droppable_index_end']
        kanban_cards = KanbanCard.objects.filter(kanban_list__id=list_id)
        kanban_card_start = kanban_cards.get(order=droppable_index_start)
        kanban_card_start.order = droppable_index_end

        kanban_card_end = kanban_cards.get(order=droppable_index_end)
        kanban_card_end.order = droppable_index_start

        kanban_card_start.save()
        kanban_card_end.save()

        return instance


class UpdateKanbanCardOrderBetweenListsSerializer(serializers.Serializer):
    list_start_id = serializers.UUIDField()
    list_end_id = serializers.UUIDField()
    droppable_index_start = serializers.IntegerField()
    droppable_index_end = serializers.IntegerField()

    def update(self, instance, validated_data):
        list_start_id = validated_data['list_start_id']
        list_end_id = validated_data['list_end_id']
        droppable_index_start = validated_data['droppable_index_start']
        droppable_index_end = validated_data['droppable_index_end']

        kanban_cards_start = KanbanCard.objects.filter(kanban_list__id=list_start_id)

        kanban_card_start = kanban_cards_start.get(order=droppable_index_start)
        # Substract 1 order starting on droppable_index_start next
        for card in kanban_cards_start:

            if card.order > droppable_index_start:
                card.order = card.order - 1
                card.save()

        kanban_cards_end = KanbanCard.objects.filter(kanban_list__id=list_end_id)

        # Add 1 order starting on droppable_index_end
        for card in kanban_cards_end:

            if card.order > droppable_index_start:
                card.order = card.order + 1
                card.save()
        kanban_card_start.kanban_list = get_object_or_404(KanbanList, id=list_end_id)
        kanban_card_start.order = droppable_index_end
        kanban_card_start.save()

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
