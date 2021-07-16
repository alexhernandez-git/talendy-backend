

# Django
from api.portals.models.portal_members import PortalMember
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q


# Django REST Framework
from api.users.models import User
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
from api.users.models import Connection

# Serializers
from api.users.serializers import ConnectionModelSerializer, ConnectInvitationSerialzer, RemoveConnectionSerializer, AcceptConnectionSerializer, IgnoreConnectionSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class ConnectionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    AddPortalMixin,
):

    queryset = Connection.objects.all()
    lookup_field = "id"
    serializer_class = ConnectionModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = (
        "follow_user__first_name",
        "follow_user__last_name",
        "follow_user__username",
        "follow_user__email",
    )

    def get_permissions(self):

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):

        user = self.request.user
        member = get_object_or_404(PortalMember, user=user, portal=self.portal)
        if self.action == "list":

            queryset = Connection.objects.filter(Q(requester=member) | Q(addressee=member), accepted=True)
        elif self.action == "list_invitations":
            queryset = Connection.objects.filter(addressee=member, accepted=False)

        return queryset

    def get_serializer_class(self):

        if self.action == "create":
            return ConnectInvitationSerialzer
        if self.action == "accept":
            return AcceptConnectionSerializer
        if self.action == "ignore":
            return IgnoreConnectionSerializer
        if self.action == "remove":
            return RemoveConnectionSerializer
        return ConnectionModelSerializer

    def get_serializer_context(self):

        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "portal": self.portal,
        }

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        follow = serializer.save()
        follow_data = ConnectionModelSerializer(follow, many=False).data
        headers = self.get_success_headers(serializer.data)
        return Response(follow_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['patch'])
    def accept(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['patch'])
    def ignore(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['patch'])
    def remove(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def list_invitations(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
