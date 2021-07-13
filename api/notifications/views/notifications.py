

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
from api.notifications.models import NotificationUser

# Serializers
from api.notifications.serializers import NotificationUserModelSerializer, ReadNotificationSerializer

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    AddPortalMixin,
):

    queryset = NotificationUser.objects.all()
    lookup_field = "id"
    serializer_class = NotificationUserModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)

    def get_permissions(self):

        permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_queryset(self):

        user = self.request.user
        user.pending_notifications = False

        user.save()
        queryset = NotificationUser.objects.filter(user=user, portal=self.portal, is_read=False)

        return queryset

    @action(detail=True, methods=['patch'])
    def read(self, request, *args, **kwargs):

        notification = self.get_object()

        partial = request.method == 'PATCH'
        serializer = ReadNotificationSerializer(
            notification,
            data=request.data,
            context={"request": request},
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
