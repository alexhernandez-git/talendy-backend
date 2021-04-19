# Django REST Framework
from rest_framework import serializers

# Models
from api.posts.models import PostMessageFile

# Serializers


class PostMessageFileModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PostMessageFile
        fields = ("id", "file", "name")

        read_only_fields = ("id",)
