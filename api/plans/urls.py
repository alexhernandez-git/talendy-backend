"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import plans as plan_views


router = DefaultRouter()
router.register(r'plans', plan_views.PlanViewSet, basename='plans')

urlpatterns = [
    path('', include(router.urls))
]
