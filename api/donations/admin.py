"""DonationItems models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.donations.models import DonationItem


@admin.register(DonationItem)
class DonationItemAdmin(admin.ModelAdmin):
    """DonationItem model admin."""

    list_display = ("price_label", "type", "currency", "stripe_price_id", "stripe_product_id")
