from api.utils.models import CModel
from django.db import models


class Order(CModel):

    offer = models.ForeignKey("orders.Offer", on_delete=models.SET_NULL,
                              related_name="order_offer", null=True, blank=True)

    buyer = models.ForeignKey("users.User", on_delete=models.SET_NULL,
                              related_name="buyer_order", null=True, blank=True)
    seller = models.ForeignKey("users.User", on_delete=models.SET_NULL,
                               related_name="seller_order", null=True, blank=True)

    karmas_amount = models.IntegerField()

    ACTIVE = 'AC'
    DELIVERED = 'DE'
    CANCELLED = 'CA'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
