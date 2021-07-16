

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer

# Models
from api.users.models import Follow, User
from api.portals.models import PortalMember


class FollowModelSerializer(serializers.ModelSerializer):

    followed_member = UserModelSerializer(read_only=True)

    class Meta:

        model = Follow
        fields = (
            "id",
            "followed_member",
        )

        read_only_fields = ("id",)


class CreateFollowSerializer(serializers.Serializer):

    followed_member = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        portal = self.context["portal"]
        from_member = get_object_or_404(PortalMember, user=request.user, portal=portal)

        user = User.objects.get(id=data["followed_member"])
        followed_member = get_object_or_404(PortalMember, user=user, portal=portal)
        # Check if is not already follow
        if from_member == followed_member:
            raise serializers.ValidationError("You can not be your follow")
        if Follow.objects.filter(from_member=from_member, followed_member=followed_member, portal=portal).exists():
            raise serializers.ValidationError("This user is already in your follows")
        return {"from_member": from_member, "followed_member": followed_member}

    def create(self, validated_data):
        from_member = validated_data["from_member"]
        portal = self.context["portal"]
        followed_member = validated_data["followed_member"]
        follow = Follow.objects.create(from_member=from_member, followed_member=followed_member, portal=portal)

        from_member.following_count += 1
        from_member.save()

        followed_member.followed_count += 1
        followed_member.save()

        return follow


class UnfollowSerializer(serializers.Serializer):

    followed_member = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        portal = self.context["portal"]
        user = User.objects.get(id=data["followed_member"])
        from_member = get_object_or_404(PortalMember, user=request.user, portal=portal)
        followed_member = get_object_or_404(PortalMember, user=user, portal=portal)

        if not Follow.objects.filter(from_member=from_member, followed_member=followed_member, portal=portal).exists():
            raise serializers.ValidationError("Your are not following this user")

        Follow.objects.filter(from_member=from_member, followed_member=followed_member).delete()
        from_member.following_count -= 1
        from_member.save()

        followed_member.followed_count -= 1
        followed_member.save()
        return data
