"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import users as user_views
from .views import contacts as contact_views
from .views import plan_payments as plan_payment_views


router = DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'contacts', contact_views.ContactViewSet, basename='contact')
router.register(r'plan-payments', plan_payment_views.PlanPaymentViewSet, basename='plan_payments')
urlpatterns = [
    path('', include(router.urls))
]
