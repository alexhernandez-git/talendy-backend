

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
from api.posts.models import PostMember


class PostMemberModelSerializer(serializers.ModelSerializer):

    user = UserModelSerializer(read_only=True)

    class Meta:

        model = PostMember
        fields = (
            "id",
            "role",
            "user",
            "created",
            "draft_rating",
            "draft_comment"
        )

        read_only_fields = ("id",)
