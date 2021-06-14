"""Plans views."""

# Django REST Framework

from rest_framework import viewsets, mixins

# Models
from api.plans.models import Plan

# Serializers
from api.plans.serializers import PlanModelSerializer


import os
from api.utils import helpers


class PlanViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Plan.objects.all()
    lookup_field = "id"
    serializer_class = PlanModelSerializer
    pagination_class = None
