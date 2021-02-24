"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.activities.models import (
    Activity,
    CancelOrderActivity,
    ChangeDeliveryTimeActivity,
    DeliveryActivity,
    IncreaseAmountActivity,
    OfferActivity,
    RevisionActivity
)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Activity model admin."""
    list_display = ("id",)


@admin.register(CancelOrderActivity)
class CancelOrderActivityAdmin(admin.ModelAdmin):
    """CancelOrderActivity model admin."""
    list_display = ("id",)


@admin.register(ChangeDeliveryTimeActivity)
class ChangeDeliveryTimeActivityAdmin(admin.ModelAdmin):
    """ChangeDeliveryTimeActivity model admin."""
    list_display = ("id",)


@admin.register(DeliveryActivity)
class DeliveryActivityAdmin(admin.ModelAdmin):
    """DeliveryActivity model admin."""
    list_display = ("id",)


@admin.register(IncreaseAmountActivity)
class IncreaseAmountActivityAdmin(admin.ModelAdmin):
    """IncreaseAmountActivity model admin."""
    list_display = ("id",)


@admin.register(OfferActivity)
class OfferActivityAdmin(admin.ModelAdmin):
    """OfferActivity model admin."""
    list_display = ("id",)


@admin.register(RevisionActivity)
class RevisionActivityAdmin(admin.ModelAdmin):
    """RevisionActivity model admin."""
    list_display = ("id",)
