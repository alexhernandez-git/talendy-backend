from api.utils.models import CModel
from django.db import models


class RequestToHelp(CModel):

    oportunity = models.ForeignKey("orders.Oportunity", on_delete=models.CASCADE, related_name="oportunity_request")
    seller = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_request")
    text = models.TextField(max_length=1000)
    accepted = models.BooleanField(default=False)
