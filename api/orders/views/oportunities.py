"""Users views."""

# Django
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
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

# Models
from api.orders.models import Oportunity

# Serializers
from api.orders.serializers import OportunityModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import os
from api.utils import helpers


class OportunityViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Oportunity.objects.all()
    lookup_field = "id"
    serializer_class = OportunityModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "title",
    )

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['retrieve']:
            permissions = []

        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def create(self, request, *args, **kwargs):

        serializer = OportunityModelSerializer(data=request.data,
                                               context={
                                                   'request': request,
                                                   'buyer': request.data['buyer']
                                               })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
