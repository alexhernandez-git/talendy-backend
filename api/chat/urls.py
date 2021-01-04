"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views

from .views import chats as contact_views


router = DefaultRouter()
router.register(r"chats", contact_views.ChatViewSet, basename="chats")

urlpatterns = [path("", include(router.urls))]
