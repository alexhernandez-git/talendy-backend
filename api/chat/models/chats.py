from api.utils.models import CModel
from django.db import models


class Chat(CModel):
    # Login Status

    room_name = models.CharField(max_length=256, blank=True, null=True)
    participants = models.ManyToManyField(
        "users.User", through="chat.Participant", verbose_name="room_participants"
    )
    last_message = models.ForeignKey(
        "chat.Message", on_delete=models.SET_NULL, null=True, related_name="last_message"
    )

    class Meta:

        ordering = ["-created"]
