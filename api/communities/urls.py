"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import communities as communities_views


router = DefaultRouter()
router.register(r'communities', communities_views.CommunityViewSet, basename='communities')

urlpatterns = [

    path('', include(router.urls))
]
