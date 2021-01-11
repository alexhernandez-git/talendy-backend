from api.utils.models import CModel
from django.db import models


class Message(CModel):
    # Login Status

    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE)
    text = models.TextField(max_length=5000)
    sent_by = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]
