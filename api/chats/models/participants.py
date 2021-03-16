from api.utils.models import CModel
from django.db import models


class Participant(CModel):

    room = models.ForeignKey("chats.Chat", on_delete=models.CASCADE)
    participant = models.ForeignKey("users.User", on_delete=models.CASCADE)
