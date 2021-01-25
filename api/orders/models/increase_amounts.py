from api.utils.models import CModel
from django.db import models


class IncreaseAmount(CModel):

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="increase_amount_order")
    issued_by = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                  related_name="increase_amount_issued_by")
    reason = models.TextField(max_length=1000)
    increase_amount = models.FloatField()
    amount_increased = models.FloatField()
