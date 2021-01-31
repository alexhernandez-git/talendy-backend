"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
# from .views import users as user_views
from .views import offers as offer_views
from .views import orders as order_views


router = DefaultRouter()
# router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'offers', offer_views.OfferViewSet, basename='offers')
router.register(r'orders', order_views.OrderViewSet, basename='orders')
urlpatterns = [
    path('', include(router.urls))
]
