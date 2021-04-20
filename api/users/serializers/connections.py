"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Serializers
from api.users.serializers import UserModelSerializer

# Models
from api.users.models import Connection, User


class ConnectionModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    requester = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Connection
        fields = (
            "id",
            "requester",
            "addressee",
        )

        read_only_fields = ("id",)


class RequestConnectionSerializer(serializers.Serializer):
    """User model serializer."""

    addressee = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        requester = request.user
        addressee = User.objects.get(id=data["addressee"])

        # Check if is not already connection
        if requester == addressee:
            raise serializers.ValidationError("You can not be your connection")
        if Connection.objects.filter(Q(requester=requester, addressee=addressee) |
                                     Q(requester=addressee, addressee=requester), accepted=True).exists():
            raise serializers.ValidationError("This user is already in your connections")

        if Connection.objects.filter(Q(requester=requester, addressee=addressee) |
                                     Q(requester=addressee, addressee=requester), accepted=False).exists():
            raise serializers.ValidationError("You have a pending invitation")
        return {"requester": requester, "addressee": addressee}

    def create(self, validated_data):
        requester = validated_data["requester"]
        addressee = validated_data["addressee"]
        connection = Connection.objects.create(requester=requester, addressee=addressee)
        return connection


class AcceptConnectionSerializer(serializers.Serializer):
    """User model serializer."""

    requester = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        addressee = request.user
        requester = User.objects.get(id=data["requester"])

        # Check if is not already connection
        if requester == addressee:
            raise serializers.ValidationError("You can not be your connection")
        if not Connection.objects.filter(requester=requester, addressee=addressee, accepted=False).exists():
            raise serializers.ValidationError("You don't have a connection request from this user")

        Connection.objects.filter(
            requester=requester, addressee=addressee, accepted=False).update(
            accepted=True)
        return data


class DeclineConnectionSerializer(serializers.Serializer):
    """User model serializer."""

    requester = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        addressee = request.user
        requester = User.objects.get(id=data["requester"])

        # Check if is not already connection
        if requester == addressee:
            raise serializers.ValidationError("You can not be your connection")
        if not Connection.objects.filter(requester=requester, addressee=addressee, accepted=False).exists():
            raise serializers.ValidationError("You don't have a connection request from this user")

        Connection.objects.filter(requester=requester, addressee=addressee, accepted=False).delete()
        return data


class UnconnectSerializer(serializers.Serializer):
    """User model serializer."""

    user = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        requester = request.user
        user = User.objects.get(id=data["user"])

        if not Connection.objects.filter(Q(requester=requester, addressee=user) |
                                         Q(requester=user, addressee=requester), accepted=True).exists():
            raise serializers.ValidationError("Your are not connected with this user")

        Connection.objects.filter(Q(requester=requester, addressee=user) |
                                  Q(requester=user, addressee=requester), accepted=True).delete()
        return data
