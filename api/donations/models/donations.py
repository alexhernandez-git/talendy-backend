from django.db.models.fields import BooleanField
from api.utils.models import CModel
from django.db import models


class Donation(CModel):
    donation_item = models.ForeignKey("donations.DonationItem", on_delete=models.CASCADE,
                                      related_name="donation_item_donation")
    from_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="from_user_donaiton")
    to_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="to_user_donation")
    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    charge_id = models.CharField(max_length=100, blank=True, null=True)

    amount_paid = models.FloatField()

    currency = models.CharField(max_length=3)
    paid = BooleanField(default=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    invoice_pdf = models.CharField(max_length=150, blank=True, null=True)
