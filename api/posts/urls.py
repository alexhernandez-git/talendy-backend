"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views


router = DefaultRouter()
urlpatterns = [
    path('', include(router.urls))
]
