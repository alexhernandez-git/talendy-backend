from api.utils.models import CModel
from django.db import models

# Models
from djmoney.models.fields import MoneyField


class MoneyReceivedActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, null=True
    )

    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
