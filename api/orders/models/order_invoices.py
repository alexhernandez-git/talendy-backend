from django.db.models.fields import BooleanField
from api.utils.models import CModel
from django.db import models

# Models
from djmoney.models.fields import MoneyField


class OrderInvoice(CModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="order_invoice")
    order_payment = models.ForeignKey("orders.OrderBilling", on_delete=models.CASCADE,
                                      related_name="order_billing_invoice")
    amount_paid = models.FloatField()
    amount_paid_usd = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)

    currency = models.CharField(max_length=3)
    paid = BooleanField(default=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    invoice_item_id = models.CharField(max_length=100, blank=True, null=True)
