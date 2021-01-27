from api.utils.models import CModel
from django.db import models


class Activity(CModel):

    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, null=True
    )

    # Orders
    OFFER = 'OF'
    CHANGE_DELIVERY_TIME = 'CT'
    INCREASE_AMOUNT = 'IA'
    DELIVERY = 'DE'
    REVISION = 'RE'
    CANCEL = 'CA'

    TYPE_CHOICES = [
        (OFFER, 'Offer order'),
        (CHANGE_DELIVERY_TIME, 'Change delivery time order'),
        (INCREASE_AMOUNT, 'Increase amount order'),
        (DELIVERY, 'Delivery order'),
        (REVISION, 'Revision order'),
        (CANCEL, 'Delivery order'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    closed = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    class Meta:

        ordering = ["-created"]
