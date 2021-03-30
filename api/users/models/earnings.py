from api.utils.models import CModel
from django.db import models

# Models
from api.plans.models import Plan
from djmoney.models.fields import MoneyField

# Utils
from django.utils import timezone


class Earning(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    TIP_REVENUE = 'TR'
    WITHDRAWN = 'WI'
    REFUND = 'RE'
    SPENT = 'SP'
    EARNING_TYPES = [
        (TIP_REVENUE, 'Tip Revenue'),
        (WITHDRAWN, 'Withdrawn'),
        (REFUND, 'Refund'),
        (SPENT, 'Spent'),
    ]

    type = models.CharField(
        max_length=2,
        choices=EARNING_TYPES,
        default=TIP_REVENUE
    )

    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    order_tip = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, blank=True, null=True)

    batch_id = models.CharField(max_length=100, blank=True, null=True)

    available_for_withdrawn_date = models.DateTimeField(
        'pending clearance expiration at',
        help_text='Date time on pending clearance ends.',
        default=timezone.now
    )

    setted_to_available_for_withdrawn = models.BooleanField(default=False)
