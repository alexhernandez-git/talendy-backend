from api.utils.models import CModel
from django.db import models


class Order(CModel):

    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="buyer_order")
    seller = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="seller_order")
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    total_amount = models.FloatField()
    is_split_payment = models.BooleanField(default=False)
    first_payment = models.FloatField()
    amount_at_delivery = models.FloatField()
    delivery_date = models.DateField()
    order_time = models.IntegerField()

    ACTIVE = 'AC'
    DELIVERED = 'DE'
    CANCELLED = 'CA'

    TYPE_CHOICES = [
        (ACTIVE, 'Active'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    status = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=ACTIVE
    )
