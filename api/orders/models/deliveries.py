from api.utils.models import CModel
from django.db import models


class Delivery(CModel):

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="delivery_order")

    response = models.TextField(max_length=1000)

    source_file = models.FileField(
        upload_to='orders/delivery/files/',
        max_length=500,
    )
