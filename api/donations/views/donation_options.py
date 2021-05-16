"""DonationOptions views."""

# Django REST Framework

from rest_framework import viewsets, mixins

# Models
from api.donations.models import DonationOption

# Serializers
from api.donations.serializers import DonationOptionModelSerializer


import os
from api.utils import helpers


class DonationOptionViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = DonationOption.objects.all()
    lookup_field = "id"
    serializer_class = DonationOptionModelSerializer
    pagination_class = None
