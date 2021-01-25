from api.utils.models import CModel
from django.db import models


class CancelOrder(CModel):

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="cancel_order_order")
    issued_by = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                  related_name="cancel_order_issued_by")
    reason = models.TextField(max_length=1000)
