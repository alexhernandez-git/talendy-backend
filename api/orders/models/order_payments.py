from api.utils.models import CModel
from django.db import models

# Models
from .orders import Order
from djmoney.models.fields import MoneyField


class OrderBilling(CModel):
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="order_billing")
    price_id = models.CharField(max_length=100, blank=True, null=True)
    unit_amount = models.FloatField()
    currency = models.CharField(max_length=3)
    service_fee = models.FloatField(null=True, blank=True)

    # Total due to seller at end of order (Normal order)
    due_to_seller = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)

    # Is first payment already paid (Two payments order)
    first_payment_paid = models.BooleanField(default=True)

    payment_at_delivery = models.FloatField()
    payment_at_delivery_currency = models.CharField(max_length=3)

    subscription_id = models.CharField(max_length=100, blank=True, null=True)
    to_be_cancelled = models.BooleanField(null=False, blank=False, default=False)
    cancelled = models.BooleanField(null=False, blank=False, default=False)
    payment_issue = models.BooleanField(null=False, blank=False, default=False)
    current_period_end = models.IntegerField(blank=True, default=0)
