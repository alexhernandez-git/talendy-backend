"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import posts as post_views
from .views import collaborate_requests as collaborate_request_views
from .views import post_messages as post_message_views
from .views import post_seen_by as post_seen_by_views
from .views import post_members as post_member_views
from .views import post_kanbans as post_kanban_views

router = DefaultRouter()
router.register(r'posts', post_views.PostViewSet, basename='posts')
router.register(r'collaborate-requests', collaborate_request_views.CollaborateRequestViewSet,
                basename='collaborate-requests')
router.register(
    r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/messages", post_message_views.PostMessageViewSet, basename="post_messages"
)
router.register(
    r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/seen-by", post_seen_by_views.PostSeenByViewSet, basename="post_seen_by"
)
router.register(
    r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/members", post_member_views.PostMemberViewSet, basename="post_members"
)
router.register(
    r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/kanbans", post_kanban_views.KanbanListViewSet, basename="post_kanbans"
)
router.register(r"posts/(?P<slug_id>[-a-zA-Z0-9_]+)/kanbans/(?P<list_slug_id>[-a-zA-Z0-9_]+)/cards",
                post_kanban_views.KanbanCardViewSet, basename="post_kanbans_cards")
urlpatterns = [
    path('', include(router.urls))
]
