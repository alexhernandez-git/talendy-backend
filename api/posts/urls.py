"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import posts as post_views

router = DefaultRouter()
router.register(r'posts', post_views.PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls))
]
