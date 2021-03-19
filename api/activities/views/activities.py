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
from api.utils.mixins import AddOrderMixin
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.db.models import Q


# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

# Models
from api.activities.models import Activity

# Serializers
from api.activities.serializers import ActivityModelSerializer

# Utils
import os
from api.utils import helpers


class ActivityViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    AddOrderMixin,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Activity.objects.all()
    lookup_field = "id"
    serializer_class = ActivityModelSerializer

    def get_queryset(self):
        have_order = False
        try:
            if self.order:
                have_order = True
                self.pagination_class = None
        except:
            pass
        if have_order:
            return Activity.objects.filter(order=self.order)
        else:
            user = self.request.user
            return Activity.objects.filter(Q(order__seller=user) | Q(order__buyer=user))

    def get_permissions(self):
        """Assign permissions based on action."""

        permissions = [IsAuthenticated]
        return [p() for p in permissions]
