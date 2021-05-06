"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import posts as post_views
from .views import contribute_requests as contribute_request_views

router = DefaultRouter()
router.register(r'posts', post_views.PostViewSet, basename='posts')
router.register(r'contribute-requests', contribute_request_views.ContributeRequestViewSet,
                basename='contribute-requests')

urlpatterns = [
    path('', include(router.urls))
]
