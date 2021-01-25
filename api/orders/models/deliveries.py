from api.utils.models import CModel
from django.db import models


class Delivery(CModel):

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="delivery_order")
    issued_by = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                  related_name="delivery_issued_by")
    description = models.TextField(max_length=1000)
    increase_amount = models.FloatField()
    amount_increased = models.FloatField()

    source_files = models.FileField(
        upload_to='orders/delivery/files/',
        max_length=500,
    )


class Images(models.Model):
    post = models.ForeignKey(Delivery, on_delete=models.CASCADE, default=None)
    image = models.ImageField('Delivery image',
                              upload_to='orders/delivery/pictures/',
                              max_length=500)
