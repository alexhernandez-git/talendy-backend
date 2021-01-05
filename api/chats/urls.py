"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views

from .views import chats as contact_views
from .views import messages as message_views


router = DefaultRouter()
router.register(r"chats", contact_views.ChatViewSet, basename="chats")
router.register(
    r"chats/(?P<slug_id>[-a-zA-Z0-9_]+)/messages", message_views.MessageViewSet, basename="messages"
)


urlpatterns = [path("", include(router.urls))]
