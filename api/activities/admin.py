"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User, Contact


# @admin.register(Contact)
# class ContactAdmin(admin.ModelAdmin):
#     """Contact model admin."""

#     list_display = ("id", "from_user", "contact_user")
