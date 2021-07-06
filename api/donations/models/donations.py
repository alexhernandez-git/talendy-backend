
from django.db.models.fields import BooleanField
from api.utils.models import CModel
from django.contrib.gis.db import models

from djmoney.models.fields import MoneyField


class Donation(CModel):
    is_other_amount = models.BooleanField(default=False)
    # If is other amount the donation item will be null
    donation_option = models.ForeignKey("donations.DonationOption", on_delete=models.SET_NULL,
                                        related_name="donation_option_donation", null=True, blank=True)
    donation_payment = models.ForeignKey("donations.DonationPayment", on_delete=models.CASCADE,
                                         related_name="donation_payment_donation")
    is_anonymous = models.BooleanField(default=False)
    email = models.CharField(max_length=100, null=True, blank=True)
    from_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="from_user_donaiton", null=True)
    to_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="to_user_donation")
    message = models.TextField(null=True, blank=True)

    gross_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    net_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    service_fee = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    rate_date = models.CharField(max_length=20, null=True, blank=True)
