from api.utils.models import CModel
from django.db import models


class RequestToConnect(CModel):
    # Login Status

    form_user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='from_user_request')
    to_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='to_user_request')
