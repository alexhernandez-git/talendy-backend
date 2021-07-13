

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import donations as donation_views
from .views import donation_options as donation_option_views


router = DefaultRouter()
router.register(r'donations', donation_views.DonationViewSet, basename='donations')
router.register(r'donation-options', donation_option_views.DonationOptionViewSet, basename='donation-options')

urlpatterns = [
    path('', include(router.urls))
]
