from api.utils.models import CModel
from django.db import models


class Connection(CModel):
    # Login Status

    user_who_has_requested = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='user_who_has_requested')
    user_who_has_accepted = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='user_who_has_accepted')
