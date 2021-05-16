from api.utils.models import CModel
from django.db import models


class DonationOption(CModel):

    LEVEL1 = 'L1'
    LEVEL2 = 'L2'
    LEVEL3 = 'L3'
    LEVEL4 = 'L4'
    TYPE_CHOICES = [
        (LEVEL1, 'Level 1'),
        (LEVEL2, 'Level 2'),
        (LEVEL3, 'Level 3'),
        (LEVEL4, 'Level 4'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    unit_amount = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    price_label = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    paid_karma = models.FloatField()
