"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import users as user_views
from .views import follows as follow_views
from .views import earnings as earning_views
from .views import connections as connection_views
from .views import reviews as review_views


router = DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'follows', follow_views.FollowViewSet, basename='follow')
router.register(r'earnings', earning_views.EarningViewSet, basename='earnings')
router.register(r'connections', connection_views.ConnectionViewSet, basename='connections')
router.register(r'reviews', review_views.ReviewViewSet, basename='reviews')
urlpatterns = [
    path('', include(router.urls))
]
