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
)

# Utils
from api.utils import helpers


class PortalMemberModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PortalMember
        fields = (
            "id",
            "portal",
            "user",
            "role",
        )

        read_only_fields = ("id",)


class CreatePortalMemberSerializer(serializers.Serializer):

    # Future me: filter email UniqueValidator by only public client
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=False,
    )

    username = serializers.CharField(
        min_length=4,
        max_length=40,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    picture = serializers.FileField(allow_empty_file=True)

    initial_karma_amount = serializers.IntegerField()

    role = serializers.CharField(min_length=2, max_length=2)

    def validate(self, data):
        import pdb
        pdb.set_trace()
        return data

    def create(self, validated_data):
        portal = self.context['portal']
        request = self.context['request']
        user = request.user
        first_name = validated_data.get('first_name', None)
        last_name = validated_data.get('last_name', None)
        email = validated_data.get('email', None)
        picture = validated_data.get('picture', None)
        initial_karma_amount = validated_data.get('initial_karma_amount', None)
        role = validated_data.get('role', None)
        # Create member
        member = PortalMember.objects.create(
            portal=portal,
            first_name=first_name,
            last_name=last_name,
            email=email,
            picture=picture,
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

        return member
