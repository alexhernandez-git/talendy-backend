"""Users views."""

# Django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Celery
from api.taskapp.tasks import send_portal_access

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
from api.portals.permissions import IsAdminOrManager

# Models
from api.portals.models import PortalMember, Portal

# Serializers
from api.portals.serializers import PortalMemberModelSerializer, CreatePortalMemberSerializer, IsMemberEmailAvailableSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Helpers

import os
from api.utils import helpers
from api.utils.mixins import AddPortalMixin
import tldextract


class PortalMemberViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    AddPortalMixin
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = PortalMember.objects.all()
    lookup_field = "id"
    serializer_class = PortalMemberModelSerializer
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('first_name', 'last_name')

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['destroy']:
            permissions = IsAdminOrManager
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['create']:
            return CreatePortalMemberSerializer
        elif self.action in ['is_member_email_available']:
            return IsMemberEmailAvailableSerializer
        return PortalMemberModelSerializer

    def get_queryset(self):
        """Restrict list to public-only."""

        queryset = PortalMember.objects.filter(portal=self.portal)

        return queryset

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "portal": self.portal
        }

    @ action(detail=False, methods=['post'])
    def is_member_email_available(self, request, *args, **kwargs):
        """Check if email passed is correct."""
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        email = serializer.data
        return Response(data=email, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.save()

        data = PortalMemberModelSerializer(data).data

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_members(self, request, *args, **kwargs):
        user = request.user
        portal = self.portal
        member_me = PortalMember.objects.get(portal=portal, user=user)
        members_ids = request.data.get('members')
        for member_id in members_ids:
            try:
                member = PortalMember.objects.get(id=member_id)
            except PortalMember.DoesNotExist:
                members_ids.remove(member_id)
                break

            # Avoid to the owner to be deleted
            if member.user == portal.owner:

                members_ids.remove(member_id)
                break

            # Avoid deletion of one manager or admin from a manager and remove an admin without been the owner
            if member.role == PortalMember.MANAGER and member_me.role == PortalMember.MANAGER or \
                    member.role == PortalMember.ADMIN and member_me.role == PortalMember.MANAGER or member.role == PortalMember.ADMIN and user != portal.owner:

                members_ids.remove(member_id)
                break

            # Substract members count

            portal.members_count -= 1
            if member.role == PortalMember.BASIC:
                portal.basic_members_count -= 1
            elif member.role == PortalMember.MANAGER:
                portal.manager_members_count -= 1
            elif member.role == PortalMember.ADMIN:
                portal.admin_members_count -= 1

            if member.is_active:
                portal.active_members_count -= 1
                if member.role == PortalMember.BASIC:
                    portal.active_basic_members_count -= 1
                elif member.role == PortalMember.MANAGER:
                    portal.active_manager_members_count -= 1
                elif member.role == PortalMember.ADMIN:
                    portal.active_admin_members_count -= 1
            portal.save()

            self.perform_destroy(member)
        return Response(data=members_ids, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def resend_access(self, request, *args, **kwargs):
        portal = self.portal
        members_ids = request.data.get('members')
        for member_id in members_ids:
            try:
                member = PortalMember.objects.get(id=member_id)
            except PortalMember.DoesNotExist:
                break

            # Send access email
            send_portal_access(member, portal)

        return Response(status=status.HTTP_204_NO_CONTENT)
