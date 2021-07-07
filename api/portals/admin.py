"""Portals models admin."""

# Django
from django.contrib import admin

# Models
from api.portals.models import Portal, PortalMember


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    """Portal model admin."""

    list_display = ("name", "url", "owner", "about", "logo",
                    "donations_enabled", "members_count", "active_members_count", "basic_members_count",
                    "active_basic_members_count",
                    "manager_members_count",
                    "active_manager_members_count",
                    "admin_members_count",
                    "active_admin_members_count",
                    "posts_count",
                    "created_posts_count",
                    "created_active_posts_count",
                    "created_solved_posts_count",
                    "collaborated_posts_count",
                    "collaborated_active_posts_count",
                    "collaborated_solved_posts_count",
                    "plan_default_payment_method",
                    "free_trial_invoiced",
                    "have_active_plan",
                    "is_free_trial",
                    "passed_free_trial_once",
                    "free_trial_expiration",
                    "is_oficial")


@admin.register(PortalMember)
class PortalMemberAdmin(admin.ModelAdmin):
    """PortalMember model admin."""

    list_display = ("id",
                    "portal",
                    "is_active",
                    "first_name",
                    "last_name",
                    "email",
                    "picture",
                    "password",)
