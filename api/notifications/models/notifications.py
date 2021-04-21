from api.utils.models import CModel
from django.db import models


class NotificationUser(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class Notification(CModel):

    MESSAGES = 'ME'
    NEW_INVITATION = 'NI'
    NEW_CONNECTION = 'NC'
    TYPE_CHOICES = [
        (MESSAGES, 'Messages'),
        (NEW_INVITATION, 'New invitation'),
        (NEW_CONNECTION, 'New connection'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    # MESSAGES
    messages = models.ManyToManyField(
        "chats.Message", blank=True, related_name="notifications_messages"
    )
    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE, null=True)

    # CONNECTIONS
    connection = models.ForeignKey("users.Connection", on_delete=models.CASCADE, null=True)

    actor = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
