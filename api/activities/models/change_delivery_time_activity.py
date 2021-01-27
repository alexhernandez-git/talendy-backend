from api.utils.models import CModel
from django.db import models


class ChangeDeliveryTimeActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    change_delivery_time = models.ForeignKey(
        "orders.ChangeDeliveryTime", on_delete=models.CASCADE
    )
