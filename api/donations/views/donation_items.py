"""DonationItems views."""

# Django REST Framework

from rest_framework import viewsets, mixins

# Models
from api.donations.models import DonationItem

# Serializers
from api.donations.serializers import DonationItemModelSerializer


import os
from api.utils import helpers


class DonationItemViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = DonationItem.objects.all()
    lookup_field = "id"
    serializer_class = DonationItemModelSerializer
    pagination_class = None
