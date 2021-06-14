from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("api/", include(("api.users.urls", "users"), namespace="users")),
    path("api/", include(("api.chats.urls", "chats"), namespace="chats")),
    path("api/", include(("api.notifications.urls", "notifications"), namespace="notifications")),
    path("api/", include(("api.donations.urls", "donations"), namespace="donations")),
    path("api/", include(("api.posts.urls", "posts"), namespace="posts")),
    path("api/", include(("api.communities.urls", "communities"), namespace="communities")),
    path("api/", include(("api.portals.urls", "portals"), namespace="portals")),
    # path(r'api/(?P<client_slug>[-a-zA-Z0-9_]+)', include(("api.users.urls", "users"), namespace="users")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
