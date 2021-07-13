

# Django REST Framework
from rest_framework import serializers

# Models
from api.plans.models import Plan


class PlanModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = Plan
        fields = (
            "id",
            "type",
            "unit_amount",
            "currency",
            "users_amount",
            "price_label"
        )

        read_only_fields = ("id",)
