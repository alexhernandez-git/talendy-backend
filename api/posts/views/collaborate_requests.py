

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
from api.users.permissions import IsAccountOwner

# Models
from api.posts.models import CollaborateRequest

# Serializers
from api.posts.serializers import (
    CollaborateRequestModelSerializer,
    RequestCollaborateSerializer,
    AcceptCollaborateRequestSerializer,
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class CollaborateRequestViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = CollaborateRequest.objects.all()
    lookup_field = "id"
    serializer_class = CollaborateRequestModelSerializer

    def get_permissions(self):

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):

        if self.action == "create":
            return RequestCollaborateSerializer

        return CollaborateRequestModelSerializer

    def get_queryset(self):

        user = self.request.user
        queryset = CollaborateRequest.objects.filter(post__user=user)

        return queryset

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collaborate_request = serializer.save()
        collaborate_request_data = CollaborateRequestModelSerializer(collaborate_request, many=False).data
        headers = self.get_success_headers(serializer.data)
        return Response(collaborate_request_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'])
    def accept(self, request, *args, **kwargs):

        collaborate_request = get_object_or_404(CollaborateRequest, id=kwargs['id'])

        partial = request.method == 'PATCH'
        serializer = AcceptCollaborateRequestSerializer(
            collaborate_request,
            data=request.data,
            context={"request": request},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
