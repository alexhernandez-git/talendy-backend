# Django REST Framework
from rest_framework import serializers

# Models
from api.tasks.models import TaskMessageFile

# Serializers


class TaskMessageFileModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = TaskMessageFile
        fields = ("id", "file", "name")

        read_only_fields = ("id",)
