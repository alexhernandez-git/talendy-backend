from api.utils.models import CModel
from django.contrib.gis.db import models

# Models
from api.donations.models import DonationOption
from djmoney.models.fields import MoneyField

# Utils
from django.utils import timezone


class KarmaEarning(CModel):
    portal = models.ForeignKey("portals.Portal", on_delete=models.SET_NULL, null=True)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    EARNED = 'EA'
    SPENT = 'SP'
    EARNING_TYPES = [
        (EARNED, 'Earned'),
        (SPENT, 'Spent'),
    ]

    type = models.CharField(
        max_length=2,
        choices=EARNING_TYPES,
    )

    amount = models.IntegerField()
