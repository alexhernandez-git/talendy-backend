from api.utils.models import CModel
from django.db import models


class Plan(CModel):

    SILVER = 'SI'
    GOLD = 'GO'
    PLATINUM = 'PL'
    TYPE_CHOICES = [
        (SILVER, 'Silver'),
        (GOLD, 'Gold'),
        (PLATINUM, 'Platinum'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    MONTHLY = 'MO'
    YEARLY = 'YE'
    INTERVAL_CHOICES = [
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]
    interval = models.CharField(
        max_length=2,
        choices=INTERVAL_CHOICES,
        default=MONTHLY
    )
    users_amount = models.IntegerField()
    unit_amount = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    price_label = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        """Meta option."""

        ordering = ['unit_amount']
