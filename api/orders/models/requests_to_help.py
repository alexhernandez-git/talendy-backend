from api.utils.models import CModel
from django.db import models


class RequestToHelp(CModel):

    offer = models.ForeignKey("orders.Offer", on_delete=models.CASCADE, related_name="offer_request")
    seller = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_request")
    text = models.TextField(max_length=1000)
    accepted = models.BooleanField(default=False)
