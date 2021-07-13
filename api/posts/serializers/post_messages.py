# Django REST Framework
from rest_framework import serializers

# Models
from api.posts.models import PostMessage, Post, PostMessageFile

# Serializers


class PostMessageModelSerializer(serializers.ModelSerializer):

    sent_by = serializers.SerializerMethodField(read_only=True)
    files = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = PostMessage
        fields = (
            "id",
            "text",
            "sent_by",
            "files",
            "created",
        )

        read_only_fields = ("id",)

    def get_sent_by(self, obj):
        from api.users.serializers import UserModelSerializer

        return UserModelSerializer(obj.sent_by, many=False).data

    def get_files(self, obj):

        from api.posts.serializers import PostMessageFileModelSerializer
        files = PostMessageFile.objects.filter(message=obj.id)
        return PostMessageFileModelSerializer(files, many=True).data


class CreatePostMessageSerializer(serializers.Serializer):

    text = serializers.CharField(max_length=1000)

    def validate(self, data):
        post = self.context["post"]
        if post.status == Post.SOLVED:
            raise serializers.ValidationError("This post has already been finalized")
        return data

    def create(self, validated_data):

        user = self.context["request"].user

        post = self.context["post"]

        message = PostMessage.objects.create(post=post, text=validated_data["text"], sent_by=user)
        post.last_message = message
        post.save()
        return message
