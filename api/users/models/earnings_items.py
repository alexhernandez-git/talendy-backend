from api.utils.models import CModel
from django.db import models

# Models
from api.plans.models import Plan
from djmoney.models.fields import MoneyField


class EarningItem(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    ORDER_REVENUE = 'OR'
    WITHDRAWN = 'WI'
    EARNING_TYPES = [
        (ORDER_REVENUE, 'Order revenue'),
        (WITHDRAWN, 'WITHDRAWN'),
    ]

    interval_subscription = models.CharField(
        max_length=2,
        choices=EARNING_TYPES,
    )
    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
