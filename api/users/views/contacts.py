"""Users views."""

# Django
import pdb
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
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from api.users.permissions import IsAccountOwner

# Models
from api.users.models import Contact

# Serializers
from api.users.serializers import (
    ContactModelSerializer,
    CreateContactSerializer
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class ContactViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Contact.objects.all()
    lookup_field = 'id'
    serializer_class = ContactModelSerializer
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('contact_user__first_name', 'contact_user__last_name', 'contact_user__username')


    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]


    def get_queryset(self):
        """Restrict list to public-only."""
        user = self.request.user
        queryset = Contact.objects.filter(from_user=user)

        return queryset

    
    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'create':
            return CreateContactSerializer
        return ContactModelSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        contact_data = ContactModelSerializer(contact, many=False).data
        headers = self.get_success_headers(serializer.data)
        return Response(contact_data, status=status.HTTP_201_CREATED, headers=headers)