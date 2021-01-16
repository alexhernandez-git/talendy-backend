"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User, Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Contact model admin."""

    list_display = ("id", "from_user", "contact_user")


class CustomUserAdmin(UserAdmin):
    """User model admin."""

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("is_verified",
                                                          "stripe_account_id", "stripe_dashboard_url")}),)
    list_display = ("email", "first_name", "last_name", "is_staff",
                    "is_client", "stripe_account_id", "stripe_dashboard_url")
    list_filter = (
        "is_client",
        "is_staff",
        "created",
        "modified",
    )


admin.site.register(User, CustomUserAdmin)
