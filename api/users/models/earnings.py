from api.utils.models import CModel
from django.contrib.gis.db import models

# Models
from api.donations.models import DonationOption
from djmoney.models.fields import MoneyField

# Utils
from django.utils import timezone


class Earning(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    DONATION_REVENUE = 'DR'
    WITHDRAWN = 'WI'
    EARNING_TYPES = [
        (DONATION_REVENUE, 'Donation Revenue'),
        (WITHDRAWN, 'Withdrawn'),
    ]

    type = models.CharField(
        max_length=2,
        choices=EARNING_TYPES,
        default=DONATION_REVENUE
    )

    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    batch_id = models.CharField(max_length=100, blank=True, null=True)

    available_for_withdrawn_date = models.DateTimeField(
        'pending clearance expiration at',
        help_text='Date time on pending clearance ends.',
        default=timezone.now
    )

    setted_to_available_for_withdrawn = models.BooleanField(default=False)
