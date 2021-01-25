from api.activities.models import StatusModel
from api.utils.models import CModel
from django.db import models


class OfferActivity(CModel, StatusModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    offer = models.ForeignKey(
        "orders.Offer", on_delete=models.CASCADE
    )
