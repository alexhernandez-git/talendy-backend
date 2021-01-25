from api.utils.models import CModel
from django.db import models
from djmoney.models.fields import MoneyField


class Offer(CModel):

    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE,
                              related_name="offer_buyer_order", null=True, blank=True)
    seller = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="offer_seller_order")
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    total_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    two_payments_order = models.BooleanField(default=False)
    first_payment = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    amount_at_delivery = models.FloatField(null=True, blank=True)
    delivery_date = models.DateTimeField()
    days_for_delivery = models.FloatField()
    accepted = models.BooleanField(default=False)
