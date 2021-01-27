from api.utils.models import CModel
from django.db import models


class CancelOrderActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    cancel_order = models.ForeignKey(
        "orders.CancelOrder", on_delete=models.CASCADE
    )
