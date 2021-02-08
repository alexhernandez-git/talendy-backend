"""User models admin."""

# Django
from django.contrib import admin

# Models
from api.orders.models import Offer, Order, OrderPayment


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Offer model admin."""

    list_display = ("id",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order model admin."""

    list_display = ("id",)


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    """Order Payment model admin."""

    list_display = ("id",)
