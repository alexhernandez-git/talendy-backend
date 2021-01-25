from api.utils.models import CModel
from django.db import models


class Revision(CModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="revision_order")
    issued_by = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                  related_name="revision_issued_by")
    reason = models.TextField(max_length=2000)
