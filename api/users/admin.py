"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User, Earning, Follow, UserLoginActivity, Connection


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Follow model admin."""

    list_display = ("id", "from_user", "followed_user")


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    """Connection model admin."""

    list_display = ("id", "requester", "addressee")


class CustomUserAdmin(UserAdmin):
    """User model admin."""

    fieldsets = UserAdmin.fieldsets + ((None,
                                        {
                                            "fields":
                                            ("is_verified", "is_online", "posts_count", "created_posts_count",
                                             "created_active_posts_count", "created_solved_posts_count",
                                             "collaborated_posts_count", "collaborated_active_posts_count",
                                             "collaborated_solved_posts_count")}),)

    list_display = ("email", "first_name", "last_name", "is_staff",
                    "is_client", "is_online")
    list_filter = (
        "is_client",
        "is_staff",
        "created",
        "modified",
        "is_online"
    )


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    """Earning model admin."""


@admin.register(UserLoginActivity)
class UserLoginActivityAdmin(admin.ModelAdmin):
    """UserLoginActivity model admin."""
    list_display = ("login_username", "created")


admin.site.register(User, CustomUserAdmin)
