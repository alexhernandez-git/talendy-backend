from api.utils.models import CModel
from django.db import models


class IncreaseAmountActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    increase_amount = models.ForeignKey(
        "orders.IncreaseAmount", on_delete=models.CASCADE
    )
