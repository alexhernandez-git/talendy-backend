"""User models admin."""

# Django
from django.contrib import admin

# Models
from api.orders.models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Offer model admin."""

    list_display = ("id",)
