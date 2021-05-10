# Django REST Framework
from rest_framework import serializers

# Models
from api.posts.models import PostSeenBy

# Serializers
from api.users.serializers import UserModelSerializer


class PostSeenByModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = PostSeenBy
        fields = ("id", "post", "message", "user", "modified")

        read_only_fields = ("id",)


class CreatePostSeenBySerializer(serializers.Serializer):
    def validate(self, data):
        post = self.context["post"]

        if not post.last_message:
            raise serializers.ValidationError("Not have last message")
        return data

    def create(self, validated_data):

        user = self.context["request"].user
        post = self.context["post"]

        seen_by, created = PostSeenBy.objects.get_or_create(post=post, user=user)
        if seen_by.message != post.last_message:

            seen_by.message = post.last_message
            seen_by.save()
        return seen_by
