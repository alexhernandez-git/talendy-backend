from django.db.models.fields import BooleanField
from api.utils.models import CModel
from django.db import models

# Models
from djmoney.models.fields import MoneyField


class OrderPayment(CModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="order_payment")
    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    charge_id = models.CharField(max_length=100, blank=True, null=True)

    amount_paid = models.FloatField()

    currency = models.CharField(max_length=3)
    paid = BooleanField(default=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    invoice_pdf = models.CharField(max_length=150, blank=True, null=True)
