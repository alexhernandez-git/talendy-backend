from api.utils.models import CModel
from django.db import models

# Models
from api.plans.models import Plan
from djmoney.models.fields import MoneyField


class Earnings(CModel):

    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    net_income = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    withdrawn = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    used_for_purchases = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    available_for_withdawal = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
