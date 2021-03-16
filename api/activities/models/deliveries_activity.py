from api.utils.models import CModel
from django.db import models


class DeliveryActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    delivery = models.ForeignKey(
        "orders.Delivery", on_delete=models.CASCADE, null=True
    )

    PENDENDT = 'PE'
    ACCEPTED = 'AC'

    TYPE_CHOICES = [
        (PENDENDT, 'Pendent'),
        (ACCEPTED, 'Accepted'),
    ]

    status = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=PENDENDT
    )
