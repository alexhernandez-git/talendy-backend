from api.utils.models import CModel
from django.db import models


class Chat(CModel):
    # Login Status

    room_name = models.CharField(max_length=256, blank=True, null=True)
    participants = models.ManyToManyField(
        "users.User", through="chats.Participant", verbose_name="room_participants"
    )
    last_message = models.ForeignKey(
        "chats.Message", on_delete=models.SET_NULL, null=True, related_name="last_message"
    )

    class Meta:

        ordering = ["-last_message__created"]
