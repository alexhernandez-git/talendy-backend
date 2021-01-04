"""Users serializers."""

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
from api.users.models import Contact, User


class ContactModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    contact_user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Contact
        fields = (
            "id",
            "contact_user",
        )

        read_only_fields = ("id",)


class CreateContactSerializer(serializers.Serializer):
    """User model serializer."""

    contact_user_id = serializers.UUIDField()

    def validate(self, data):
        request = self.context["request"]
        from_user = request.user
        contact_user = User.objects.get(id=data["contact_user_id"])

        # Check if is not already contact
        if from_user == contact_user:
            raise serializers.ValidationError("You can not be your contact")
        if Contact.objects.filter(from_user=from_user, contact_user=contact_user).exists():
            raise serializers.ValidationError("This user is already in your contacts")
        return {"from_user": from_user, "contact_user": contact_user}

    def create(self, validated_data):
        from_user = validated_data["from_user"]
        contact_user = validated_data["contact_user"]
        contact = Contact.objects.create(from_user=from_user, contact_user=contact_user)
        return contact
