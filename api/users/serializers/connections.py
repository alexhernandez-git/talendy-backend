"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Serializers
from api.users.serializers import UserModelSerializer

# Models
from api.users.models import Connection, User
from api.notifications.models import Notification, NotificationUser


class ConnectionModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    requester = UserModelSerializer(read_only=True)
    addressee = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Connection
        fields = (
            "id",
            "requester",
            "addressee",
        )

        read_only_fields = ("id",)


class ConnectInvitationSerialzer(serializers.Serializer):
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

        # Notificate the invitation to the addressee
        notification = Notification.objects.create(
            type=Notification.NEW_INVITATION,
            connection=connection,
        )
        user_notification = NotificationUser.objects.create(
            notification=notification,
            user=addressee
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % addressee.id, {
                "type": "send.notification",
                "event": "NEW_INVITATION",
                "notification__pk": str(user_notification.pk),
            }
        )
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
            raise serializers.ValidationError("You don't have a connect invitation from this user")

        connection = Connection.objects.filter(
            requester=requester, addressee=addressee, accepted=False).first()
        connection.accepted = True
        connection.save()
        # Notificate the new connection to the users
        notification = Notification.objects.create(
            type=Notification.NEW_CONNECTION,
            connection=connection,
        )

        user_notification = NotificationUser.objects.create(
            notification=notification,
            user=requester
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % requester.id, {
                "type": "send.notification",
                "event": "NEW_CONNECTION",
                "notification__pk": str(user_notification.pk),
            }
        )
        return data


class IgnoreConnectionSerializer(serializers.Serializer):
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
            raise serializers.ValidationError("You don't have a connect invitation from this user")

        Connection.objects.filter(requester=requester, addressee=addressee, accepted=False).delete()
        return data


class RemoveConnectionSerializer(serializers.Serializer):
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
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % user.id, {
                "type": "send.notification",
                "event": "CONNECTION_REMOVED",
            }
        )
        return data
