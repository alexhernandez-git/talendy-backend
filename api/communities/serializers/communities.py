"""Notifications serializers."""

# Django REST Framework
from rest_framework import serializers

# Django


# Serializers


# Models
from api.communities.models import Community


class CommunityModelSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""

        model = Community
        fields = (
            "id",
            "name"
        )

        read_only_fields = ("id",)
