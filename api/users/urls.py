"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import users as user_views
from .views import followed as follow_views
from .views import plan_payments as plan_payment_views
from .views import earnings as earning_views


router = DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'followed', follow_views.ContactViewSet, basename='follow')
router.register(r'earnings', earning_views.EarningViewSet, basename='earnings')
urlpatterns = [
    path('', include(router.urls))
]
