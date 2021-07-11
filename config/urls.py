from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/", include(("api.users.urls", "users"), namespace="users")),
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/", include(("api.chats.urls", "chats"), namespace="chats")),
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/",
            include(("api.notifications.urls", "notifications"),
                    namespace="notifications")),
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/",
            include(("api.donations.urls", "donations"), namespace="donations")),
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/", include(("api.posts.urls", "posts"), namespace="posts")),
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/", include(("api.portals.urls", "portals"), namespace="portals")),
    re_path(r"api/(?P<portal_url>[-a-zA-Z0-9_]+)/", include(("api.plans.urls", "plans"), namespace="plans")),
    # re_path(r'api/(?P<client_slug>[-a-zA-Z0-9_]+)', include(("api.users.urls", "users"), namespace="users")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
