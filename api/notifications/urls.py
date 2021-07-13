

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import notifications as notification_views


router = DefaultRouter()
router.register(r'notifications', notification_views.NotificationViewSet, basename='notifications')
urlpatterns = [
    path('', include(router.urls))
]
