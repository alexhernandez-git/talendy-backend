"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User


class CustomUserAdmin(UserAdmin):
    """User model admin."""
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_verified',)}),
    )
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'is_client')
    list_filter = ('is_client', 'is_staff', 'created',
                   'modified', )


admin.site.register(User, CustomUserAdmin)
