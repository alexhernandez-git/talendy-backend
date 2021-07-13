

# Django
from django.shortcuts import get_object_or_404

# Django REST Framework
from rest_framework import serializers

# Models
from api.posts.models import PostFile, PostFolder, Post
from api.users.models import User

# Serializers
from .post_folders import TopPostFolderModelSerializer


class PostFileModelSerializer(serializers.ModelSerializer):

    top_folder = TopPostFolderModelSerializer(read_only=True)

    class Meta:

        model = PostFile
        fields = (
            'id',
            'name',
            'code',
            'is_private',
            'file',
            'top_folder',
        )

        read_only_fields = (
            'id',
        )

    def validate(self, data):
        post = self.context['post']
        file = data['file']
        # Check if all files are not more than 1 Gb
        if (post.files_size + file.size) > 1073741824:
            raise serializers.ValidationError("You cannot store more than 2 GB in a single post")

        if post.status == Post.SOLVED:
            raise serializers.ValidationError("This post has already been finalized")
        return data

    def create(self, validated_data):
        post = self.context['post']
        validated_data['post'] = post
        file = validated_data['file']
        validated_data['size'] = file.size
        post.files_size += file.size
        post.save()
        if self.context['top_folder']:
            validated_data['top_folder'] = PostFolder.objects.get(
                pk=self.context['top_folder'])
        return super().create(validated_data)


class MovePostFilesSerializer(serializers.Serializer):

    top_folder = serializers.CharField()

    def validate(self, data):
        if 'top_folder' in data:
            top_folder = data['top_folder']
            top_folder = get_object_or_404(PostFolder, pk=top_folder)
        else:
            top_folder = None

        return {
            'top_folder': top_folder,
        }

    def update(self, instance, validated_data):
        # post = validated_data['post']
        top_folder = validated_data['top_folder']

        instance.top_folder = top_folder
        instance.save()

        return instance
