from api.utils.models import CModel
from django.db import models

# Models
from api.plans.models import Plan
from djmoney.models.fields import MoneyField


class Earning(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    ORDER_REVENUE = 'OR'
    WITHDRAWN = 'WI'
    EARNING_TYPES = [
        (ORDER_REVENUE, 'Order revenue'),
        (WITHDRAWN, 'Withdrawn'),
    ]

    type = models.CharField(
        max_length=2,
        choices=EARNING_TYPES,
        default=ORDER_REVENUE
    )

    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    batch_id = models.CharField(max_length=100, blank=True, null=True)
