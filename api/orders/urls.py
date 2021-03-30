"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
# from .views import users as user_views
from .views import oportunities as oportunity_views
from .views import orders as order_views
from .views import deliveries as delivery_views
from .views import cancel_orders as cancel_order_views
from .views import revisions as revision_views


router = DefaultRouter()
# router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'oportunities', oportunity_views.OportunityViewSet, basename='oportunities')
router.register(r'orders', order_views.OrderViewSet, basename='orders')
router.register(r'orders/(?P<order_id>[-a-zA-Z0-9_]+)/deliveries',
                delivery_views.DeliveryViewSet, basename='deliveries')
router.register(r'orders/(?P<order_id>[-a-zA-Z0-9_]+)/cancel-orders',
                cancel_order_views.CancelOrderViewSet, basename='cancel_orders')
router.register(r'orders/(?P<order_id>[-a-zA-Z0-9_]+)/revisions',
                revision_views.RevisionViewSet, basename='revisions')
urlpatterns = [
    path('', include(router.urls))
]
