"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User, Earning, Contact, PlanPayment, PlanSubscription, UserLoginActivity


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Contact model admin."""

    list_display = ("id", "from_user", "contact_user")


class CustomUserAdmin(UserAdmin):
    """User model admin."""

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("is_verified", "stripe_account_id", "stripe_dashboard_url", "stripe_customer_id",
                                                          "net_income", "withdrawn", "used_for_purchases", "available_for_withdawal", "active_month")}),)
    list_display = ("email", "first_name", "last_name", "is_staff",
                    "is_client", "stripe_account_id", "stripe_dashboard_url")
    list_filter = (
        "is_client",
        "is_staff",
        "created",
        "modified",
    )


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    """Earning model admin."""


@admin.register(PlanPayment)
class PlanPaymentAdmin(admin.ModelAdmin):
    """PlanPayment model admin."""


@admin.register(PlanSubscription)
class PlanSubscriptionAdmin(admin.ModelAdmin):
    """PlanSubscription model admin."""


@admin.register(UserLoginActivity)
class UserLoginActivityAdmin(admin.ModelAdmin):
    """UserLoginActivity model admin."""
    list_display = ("login_username", "created")


admin.site.register(User, CustomUserAdmin)
