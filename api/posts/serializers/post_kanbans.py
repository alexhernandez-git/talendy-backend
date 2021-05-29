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
        read_only_fields = ("created",)

    def validate(self, data):

        user = self.context['request'].user
        list = self.context['list']

        if not list.post.members.filter(user=user).exists():
            raise serializers.ValidationError("Not enough karma offered")

        return data

    def create(self, validated_data):

        list = self.context['list']
        title = validated_data["title"]
        id = validated_data["id"]
        # Get the kanban card higher order number
        order = 0
        if KanbanCard.objects.filter(list=list).order_by("-order").exists():
            last_kanban_card = KanbanCard.objects.filter(list=list).order_by("-order").exists()
            order = ++last_kanban_card.order
        card = KanbanCard.objects.create(id=id, title=title, list=list, order=order)

        return card


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

        read_only_fields = ("created",)

    def get_cards(self, obj):
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
        id = validated_data["id"]
        # Get the kanban list higher order number
        order = 0
        if KanbanList.objects.filter(post=post).order_by("-order").exists():
            last_kanban_list = KanbanList.objects.filter(post=post).order_by("-order").first()

            order = ++last_kanban_list.order
        list = KanbanList.objects.create(id=id, title=title, post=post, order=order)

        return list
