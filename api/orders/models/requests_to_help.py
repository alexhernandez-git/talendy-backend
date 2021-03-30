from api.utils.models import CModel
from django.db import models


class RequestToHelp(CModel):

    send_offer_by_email = models.BooleanField(default=False)
    offer = models.ForeignKey("orders.Offer", on_delete=models.CASCADE, related_name="offer_request")
    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_request")
    text = models.TextField(max_length=1000)
