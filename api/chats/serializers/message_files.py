# Django REST Framework
from rest_framework import serializers

# Models
from api.chats.models import MessageFile

# Serializers


class MessageFileModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = MessageFile
        fields = ("id", "file", "name")

        read_only_fields = ("id",)
