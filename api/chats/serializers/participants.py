# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import Participant

# Serializers
from api.users.serializers import UserModelSerializer


class ParticipantModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Participant
        fields = (
            "id",
            "participant",
        )

        read_only_fields = ("id",)
