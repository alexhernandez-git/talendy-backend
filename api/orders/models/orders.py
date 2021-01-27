from api.utils.models import CModel
from django.db import models

from djmoney.models.fields import MoneyField


class Order(CModel):

    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="buyer_order")
    seller = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="seller_order")
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    total_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    first_payment = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    last_payment = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)

    delivery_date = models.DateTimeField()

    order_time = models.IntegerField()

    TWO_PAYMENTS_ORDER = 'TP'
    NORMAL_ORDER = 'NO'
    RECURRENT_ORDER = 'RO'
    TYPE_CHOICES = [
        (NORMAL_ORDER, 'Two payments order'),
        (TWO_PAYMENTS_ORDER, 'Two payments order'),
        (RECURRENT_ORDER, 'Recurrent order'),
    ]

    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    ANNUAL = 'AN'
    MONTH = 'MO'
    INTERVAL_CHOICES = [
        (ANNUAL, 'Annual'),
        (MONTH, 'Month'),
    ]

    interval_subscription = models.CharField(
        max_length=2,
        choices=INTERVAL_CHOICES,
        default=MONTH
    )

    ACTIVE = 'AC'
    DELIVERED = 'DE'
    CANCELLED = 'CA'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=ACTIVE
    )
