"""Users serializers."""

# Django REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer
from api.posts.serializers import PostModelSerializer

# Models
from api.portals.models import Portal
from api.users.models import User


class PortalModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Portal
        fields = (
            "id",
            "name",
            "url",
            "donations_enabled"
        )

        read_only_fields = ("id",)


class CreatePortalSerializer(serializers.Serializer):

    name = serializers.CharField(
        min_length=4,
        max_length=140,
        validators=[UniqueValidator(queryset=Portal.objects.all())],

    )

    url = serializers.SlugField(
        min_length=3,
        max_length=40,
        validators=[UniqueValidator(queryset=Portal.objects.all())],
    )

    about = serializers.CharField(allow_blank=True)

    logo = serializers.FileField(allow_empty_file=True)

    # User login in case user is not authenticate
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=False,
        allow_blank=True
    )

    username = serializers.CharField(
        min_length=4,
        max_length=40,
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=False,
        allow_blank=True

    )
    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: +999999999. Up to 15 digits allowed.",
        required=False,
        allow_blank=True

    )
    phone_number = serializers.CharField(
        validators=[phone_regex], required=False, allow_blank=True)

    # Password
    password = serializers.CharField(min_length=8, max_length=64, required=False, allow_blank=True)
    password_confirmation = serializers.CharField(min_length=8, max_length=64, required=False, allow_blank=True)

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(min_length=2, max_length=30, required=False, allow_blank=True)

    # Currency for seller subscription
    currency = serializers.CharField(max_length=3, required=False, allow_blank=True)

    def validate(self, data):
        request = self.context['request']
        if not request.user.id:
            passwd = data['password']
            passwd_conf = data['password_confirmation']

            if passwd != passwd_conf:
                raise serializers.ValidationError('Password do not match')

        return data
