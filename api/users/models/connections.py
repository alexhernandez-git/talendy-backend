from api.utils.models import CModel
from django.db import models


class Connection(CModel):
    # Login Status

    requester = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='requester')
    addressee = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='addressee')
    accepted = models.BooleanField(default=False)
