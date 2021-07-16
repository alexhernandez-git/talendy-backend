

# Django
from api.utils.mixins import AddPortalMixin
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
from api.users.models import Earning

# Serializers
from api.users.serializers import EarningModelSerializer, WithdrawFundsModelSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


import os
from api.utils import helpers


class EarningViewSet(
    mixins.ListModelMixin,
    AddPortalMixin
):

    queryset = Earning.objects.all()
    lookup_field = "id"
    serializer_class = EarningModelSerializer

    def get_permissions(self):

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):

        user = self.request.user

        queryset = Earning.objects.filter(user=user)
        return queryset

    @action(detail=False, methods=['post'])
    def withdraw_funds(self, request, *args, **kwargs):

        serializer = WithdrawFundsModelSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        withdrawn = serializer.save()

        data = EarningModelSerializer(withdrawn, many=False).data

        return Response(data, status=status.HTTP_201_CREATED)
