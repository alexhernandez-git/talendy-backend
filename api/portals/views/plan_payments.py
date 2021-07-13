

# Django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
from api.users.models import User
import stripe
import json
import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.users.permissions import IsAccountOwner

# Models
from api.portals.models import PlanPayment, Portal

# Serializers
from api.portals.serializers import PlanPaymentModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Helpers

import os
from api.utils import helpers
from api.utils.mixins import AddPortalMixin
import tldextract


class PlanPaymentViewSet(
    mixins.ListModelMixin,
    AddPortalMixin
):

    queryset = PlanPayment.objects.all()
    lookup_field = "id"
    serializer_class = PlanPaymentModelSerializer

    def get_permissions(self):

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):

        queryset = PlanPayment.objects.filter(portal=self.portal)

        return queryset
