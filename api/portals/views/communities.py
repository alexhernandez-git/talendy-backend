

# Django
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import F

# Django REST Framework
import stripe
import json
import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from api.utils.mixins import AddPortalMixin
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
from api.portals.models import Community

# Serializers
from api.portals.serializers import CommunityModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class CommunityViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    AddPortalMixin,
):

    queryset = Community.objects.all()
    lookup_field = "id"
    serializer_class = CommunityModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    pagination_class = None

    def get_queryset(self):

        queryset = Community.objects.filter(portal=self.portal).order_by('created')

        return queryset