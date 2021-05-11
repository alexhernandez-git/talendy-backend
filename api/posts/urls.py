"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import posts as post_views
from .views import contribute_requests as contribute_request_views
from .views import post_messages as post_message_views
from .views import post_seen_by as post_seen_by_views

router = DefaultRouter()
router.register(r'posts', post_views.PostViewSet, basename='posts')
router.register(r'contribute-requests', contribute_request_views.ContributeRequestViewSet,
                basename='contribute-requests')
router.register(
    r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/messages", post_message_views.PostMessageViewSet, basename="post_messages"
)
router.register(
    r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/seen-by", post_seen_by_views.PostSeenByViewSet, basename="post_seen_by"
)
urlpatterns = [
    path('', include(router.urls))
]
