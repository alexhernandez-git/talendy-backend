# Django REST Framework
from rest_framework import serializers

# Models
from api.posts.models import PostMessage, PostMessageFile

# Serializers


class PostMessageFileModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = PostMessageFile
        fields = ("id", "file", "name")

        read_only_fields = ("id",)
