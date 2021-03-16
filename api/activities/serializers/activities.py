# Django REST Framework
from rest_framework import serializers

# Models
from api.activities.models import (
    Activity,
    CancelOrderActivity,
    ChangeDeliveryTimeActivity,
    DeliveryActivity,
    IncreaseAmountActivity,
    OfferActivity,
    RevisionActivity,

)

# Serializers
from .offers_activity import OfferActivityModelSerializer
from api.utils import helpers


class ActivityModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    activity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Activity
        fields = (
            "id",
            "type",
            "activity",
            "created"
        )

        read_only_fields = ("id",)

    def get_activity(self, obj):

        model, serializer = helpers.get_activity_classes(obj.type)

        if model and serializer:
            activity_queryset = model.objects.filter(activity=obj)

            if activity_queryset.exists():

                return serializer(activity_queryset.first(), many=False).data
        return None
