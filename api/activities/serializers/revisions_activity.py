# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import RevisionActivity

# Serializers
from api.orders.serializers import RevisionModelSerializer


class RevisionActivityModelSerializer(serializers.ModelSerializer):
    """Offer model serializer."""
    revision = RevisionModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = RevisionActivity
        fields = (
            "id",
            "revision",
        )

        read_only_fields = ("id",)
