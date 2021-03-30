from api.utils.models import CModel
from django.db import models


class RequestToHelpActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    request_to_help = models.ForeignKey(
        "orders.RequestToHelp", on_delete=models.CASCADE
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
