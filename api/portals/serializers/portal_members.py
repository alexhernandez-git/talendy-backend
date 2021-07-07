"""Users serializers."""

# Django REST Framework

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point

# Serializers
from api.users.serializers import UserModelSerializer
from api.posts.serializers import PostModelSerializer
from api.plans.serializers import PlanModelSerializer

# Models
from api.portals.models import PortalMember, PlanSubscription
from api.users.models import User, UserLoginActivity, Earning, Connection, Follow, Blacklist, KarmaEarning
from api.plans.models import Plan


# Celery
from api.taskapp.tasks import (
    send_confirmation_email,
    send_portal_access,
)

# Utils
from api.utils import helpers


class PortalMemberModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = PortalMember
        fields = (
            "id",
            "portal",
            "user",
            "is_active",
            "first_name",
            "last_name",
            "email",
            "picture",
            "password",
            "karma_amount",
            "karma_refunded",
            "karma_earned",
            "karma_earned_by_posts",
            "karma_earned_by_join_portal",
            "karma_earned_by_donations",
            "karma_spent",
            "karma_ratio",
            "following_count",
            "connections_count",
            "invitations_count",
            "followed_count",
            "posts_count",
            "created_posts_count",
            "created_active_posts_count",
            "created_solved_posts_count",
            "collaborated_posts_count",
            "collaborated_active_posts_count",
            "collaborated_solved_posts_count",
            "role",
        )

        read_only_fields = ("id",)


class CreatePortalMemberSerializer(serializers.Serializer):

    # Future me: filter email UniqueValidator by only public client
    email = serializers.CharField()

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    initial_karma_amount = serializers.IntegerField()

    role = serializers.CharField(min_length=2, max_length=2)

    def validate(self, data):
        portal = self.context['portal']

        # Check if this member already exists
        email = data.get('email')
        if PortalMember.objects.filter(portal=portal, email=email).exists():
            raise serializers.ValidationError("This email already exists in your members")

        return data

    def create(self, validated_data):
        portal = self.context['portal']
        request = self.context['request']
        user = request.user
        first_name = validated_data.get('first_name', None)
        last_name = validated_data.get('last_name', None)
        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        initial_karma_amount = validated_data.get('initial_karma_amount', None)
        role = validated_data.get('role', None)
        # Create member
        member = PortalMember.objects.create(
            portal=portal,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            initial_karma_amount=initial_karma_amount,
            role=role,
            creator=user
        )
        # Update portal info
        portal.members_count += 1
        if role == PortalMember.BASIC:
            portal.basic_members_count += 1
        elif role == PortalMember.MANAGER:
            portal.manager_members_count += 1
        elif role == PortalMember.ADMIN:
            portal.admin_members_count += 1

        portal.save()
        # Send portal access email
        send_portal_access(member, portal)
        return member


class IsMemberEmailAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']
        portal = self.context['portal']

        if PortalMember.objects.filter(portal=portal, email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        return {"email": email}
