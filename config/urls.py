from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("api/", include(("api.users.urls", "users"), namespace="users")),
    path("api/", include(("api.chats.urls", "chats"), namespace="chats")),
    path("api/", include(("api.notifications.urls", "notifications"), namespace="notifications")),
    path("api/", include(("api.plans.urls", "plans"), namespace="plans")),
    path("api/", include(("api.orders.urls", "orders"), namespace="orders")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
