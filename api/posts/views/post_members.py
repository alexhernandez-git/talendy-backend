

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
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.posts.permissions import IsPostOwnerPostMembers


# Models
from api.posts.models import PostMember

# Serializers
from api.posts.serializers import PostMemberModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import os
from api.utils import helpers


class PostMemberViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = PostMember.objects.all()
    lookup_field = "id"
    serializer_class = PostMemberModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)

    def get_permissions(self):

        if self.action in ['update']:
            permissions = [IsAuthenticated, IsPostOwnerPostMembers]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]
