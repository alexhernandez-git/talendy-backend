from api.utils.models import CModel
from django.db import models


class ChangeDeliveryTime(CModel):

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="change_delivery_time_order")
    issued_by = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                  related_name="change_delivery_time_issued_by")
    reason = models.TextField(max_length=1000)
    new_delivery_date = models.DateField()
    new_order_time = models.IntegerField()
