from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("api/", include(("api.users.urls", "users"), namespace="users")),
    path("api/", include(("api.chats.urls", "chat"), namespace="chat")),
    path("api/", include(("api.notifications.urls", "notification"), namespace="notification")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
