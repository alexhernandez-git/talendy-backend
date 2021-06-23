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
from api.portals.models import PlanSubscription
from api.users.models import User, UserLoginActivity, Earning, Connection, Follow, Blacklist, KarmaEarning
from api.plans.models import Plan


# Celery
from api.taskapp.tasks import (
    send_confirmation_email,
)

# Utils
from api.utils import helpers


class PlanSubscriptionModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PlanSubscription
        fields = (
            "id",
            "user",
            "portal",
            "subscription_id",
            "status",
            "product_id",
            "to_be_cancelled",
            "cancelled",
            "payment_issue",
            "coupon",
            "current_period_end",
            "plan_type",
            "plan_unit_amount",
            "plan_currency",
            "plan_price_label",
            "interval",
        )

        read_only_fields = ("id",)
