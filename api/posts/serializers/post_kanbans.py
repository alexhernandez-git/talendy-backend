

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

    class Meta:

        model = KanbanCard
        fields = (
            "id",
            "title",
        )
        read_only_fields = ("created",)

    def validate(self, data):

        user = self.context['request'].user
        kanban_list = self.context['kanban_list']

        if not kanban_list.post.members.filter(id=user.id).exists():
            raise serializers.ValidationError("You are not a member of this post")

        return data

    def create(self, validated_data):

        kanban_list = self.context['kanban_list']
        title = validated_data["title"]
        id = validated_data["id"]
        # Get the kanban card higher order number
        order = 0
        if KanbanCard.objects.filter(kanban_list=kanban_list).order_by("-order").exists():
            last_kanban_card = KanbanCard.objects.filter(kanban_list=kanban_list).order_by("-order").first()
            order = last_kanban_card.order + 1

        card = KanbanCard.objects.create(id=id, title=title, kanban_list=kanban_list, order=order)

        return card


class KanbanListModelSerializer(serializers.ModelSerializer):

    cards = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = KanbanList
        fields = (
            "id",
            "title",
            "cards",
        )

        read_only_fields = ("created",)

    def get_cards(self, obj):
        return KanbanCardModelSerializer(KanbanCard.objects.filter(kanban_list=obj.id), many=True).data

    def validate(self, data):
        user = self.context['request'].user
        post = self.context['post']

        if not post.members.filter(id=user.id).exists():
            raise serializers.ValidationError("You are not a member of this post")

        return data

    def create(self, validated_data):

        post = self.context['post']
        title = validated_data["title"]
        id = validated_data["id"]
        # Get the kanban list higher order number
        order = 0
        if KanbanList.objects.filter(post=post).order_by("-order").exists():
            last_kanban_list = KanbanList.objects.filter(post=post).order_by("-order").first()

            order = last_kanban_list.order + 1
        list = KanbanList.objects.create(id=id, title=title, post=post, order=order)

        return list
