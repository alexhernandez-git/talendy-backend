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

    REFUNDED = 'RE'
    EARNED_BY_DONATION = 'ED'
    EARNED_BY_JOIN_PORTAL = 'ED'
    EARNED = 'EA'
    SPENT = 'SP'
    EARNING_TYPES = [
        (REFUNDED, 'Refunded'),
        (EARNED_BY_DONATION, 'Earned by donation'),
        (EARNED, 'Earned'),
        (SPENT, 'Spent'),
    ]

    type = models.CharField(
        max_length=2,
        choices=EARNING_TYPES,
    )

    amount = models.IntegerField()
