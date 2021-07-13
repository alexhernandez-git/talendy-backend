

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import portals as portal_views
from .views import plan_payments as plan_payment_views
from .views import portal_members as portal_member_views
from .views import communities as community_views
from .views import dashboard_communities as dashboard_community_views


router = DefaultRouter()
router.register(r'portals', portal_views.PortalViewSet, basename='portals')
router.register(r'members', portal_member_views.PortalMemberViewSet, basename='members')
router.register(r'plan-payments', plan_payment_views.PlanPaymentViewSet, basename='plan_payments')
router.register(r'communities', community_views.CommunityViewSet, basename='communities')
router.register(r'dashboard-communities', dashboard_community_views.CommunityViewSet, basename='dashboard-communities')

urlpatterns = [
    path('', include(router.urls))
]
