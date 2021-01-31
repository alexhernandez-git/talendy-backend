from api.utils.models import CModel
from django.db import models

# Models
from .orders import Order
from djmoney.models.fields import MoneyField


class Offer(CModel):

    type = models.CharField(
        max_length=2,
        choices=Order.TYPE_CHOICES,
    )
    interval_subscription = models.CharField(
        max_length=2,
        choices=Order.INTERVAL_CHOICES,
        default=Order.MONTH
    )
    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE,
                              related_name="offer_buyer_order", null=True, blank=True)
    send_offer_by_email = models.BooleanField(default=False)
    buyer_email = models.CharField(max_length=150, null=True, blank=True)
    seller = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="offer_seller_order")
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    unit_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    first_payment = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    payment_at_delivery = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_time = models.IntegerField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
