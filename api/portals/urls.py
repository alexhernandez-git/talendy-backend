"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import portals as portal_views


router = DefaultRouter()
router.register(r'portals', portal_views.PortalViewSet, basename='portals')

urlpatterns = [
    path('', include(router.urls))
]