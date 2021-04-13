"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import donations as donation_views
from .views import donation_items as donation_items_views


router = DefaultRouter()
router.register(r'donations', donation_views.DonationViewSet, basename='donations')
router.register(r'donation-items', donation_items_views.DonationItemViewSet, basename='donation-items')

urlpatterns = [
    path('', include(router.urls))
]
