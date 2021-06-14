from django.db.models.fields import BooleanField
from api.utils.models import CModel
from django.db import models


class PlanPayment(CModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    portal = models.ForeignKey("portals.Portal", on_delete=models.CASCADE)
    subscription = models.ForeignKey("portals.PlanSubscription", on_delete=models.SET_NULL, blank=True, null=True)

    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    charge_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_id = models.CharField(max_length=100, blank=True, null=True)

    amount_paid = models.FloatField()

    currency = models.CharField(max_length=3)
    paid = BooleanField(default=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    invoice_pdf = models.CharField(max_length=150, blank=True, null=True)
