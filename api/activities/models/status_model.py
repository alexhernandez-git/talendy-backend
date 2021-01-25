from api.utils.models import CModel
from django.db import models


class StatusModel(models.Model):

    PENDENDT = 'PE'
    ACCEPTED = 'AC'
    CANCELLED = 'CA'

    TYPE_CHOICES = [
        (PENDENDT, 'Pendent'),
        (ACCEPTED, 'Accepted'),
        (CANCELLED, 'Cancelled'),
    ]

    status = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=PENDENDT

    )

    closed = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
