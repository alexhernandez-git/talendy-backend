"""User models admin."""

# Django
from django.contrib import admin

# Models
from api.orders.models import Oportunity, Order, OrderTip, Revision, CancelOrder, Delivery


@admin.register(Oportunity)
class OportunityAdmin(admin.ModelAdmin):
    """Oportunity model admin."""

    list_display = ("id",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order model admin."""

    list_display = ("id",)


@admin.register(OrderTip)
class OrderTipAdmin(admin.ModelAdmin):
    """Order Payment model admin."""

    list_display = ("id",)


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    """Order Revision model admin."""

    list_display = ("id",)


@admin.register(CancelOrder)
class CancelOrderAdmin(admin.ModelAdmin):
    """Order CancelOrder model admin."""

    list_display = ("id",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Order Delivery model admin."""

    list_display = ("id",)
