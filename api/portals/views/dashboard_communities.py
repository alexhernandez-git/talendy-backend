

# Django
import pdb
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import F
from api.portals.permissions import IsAdminOrManager

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
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    AddPortalMixin,
):

    queryset = Community.objects.all()
    lookup_field = "id"
    serializer_class = CommunityModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)

    def get_queryset(self):

        queryset = Community.objects.filter(portal=self.portal)

        return queryset

    def get_permissions(self):

        permissions = [IsAdminOrManager]

        return [p() for p in permissions]

    def get_serializer_context(self):

        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "portal": self.portal,
        }

    @action(detail=False, methods=['post'])
    def remove_communities(self, request, *args, **kwargs):
        portal = self.portal
        communities_ids = request.data.get('communities')
        for community_id in communities_ids:
            community = None
            try:
                community = Community.objects.get(id=community_id)
            except Community.DoesNotExist:
                communities_ids.remove(community_id)
                break

            self.perform_destroy(community)
            portal.communities_count -= 1
            portal.save()
        return Response(data=communities_ids, status=status.HTTP_200_OK)
