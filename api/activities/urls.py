"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
# from .views import users as user_views
# from .views import follows as follow_views
from .views import activities as activity_views

router = DefaultRouter()
# router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'activities',
                activity_views.ActivityViewSet, basename='activities')
# router.register(
#     r'activities/(?P<order_id>[-a-zA-Z0-9_]+)/',
#     activity_views.ActivityViewSet,
#     basename='activities'
# )
urlpatterns = [
    path('', include(router.urls))
]
