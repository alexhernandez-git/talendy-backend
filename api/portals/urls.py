"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import portals as portal_views
from .views import plan_payments as plan_payment_views


router = DefaultRouter()
router.register(r'portals', portal_views.PortalViewSet, basename='portals')
router.register(r'plan-payments', plan_payment_views.PlanPaymentViewSet, basename='plan_payments')

urlpatterns = [
    path('', include(router.urls))
]
