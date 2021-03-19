from api.utils.models import CModel
from django.db import models


class Message(CModel):
    # Login Status

    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE)
    text = models.TextField(max_length=5000, null=True, blank=True)
    sent_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.ForeignKey("activities.Activity", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["-created"]
