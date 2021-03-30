# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import RequestToHelpActivity

# Serializers
from api.orders.serializers import RequestToHelpSerializer


class RequestToHelpActivitySerializer(serializers.ModelSerializer):
    """Oportunity model serializer."""
    request_to_help = RequestToHelpSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = RequestToHelpActivity
        fields = (
            "id",
            "request_to_help",
            "status"
        )

        read_only_fields = ("id",)
