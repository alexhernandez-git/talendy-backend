from api.utils.models import CModel
from django.db import models


class NotificationUser(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class Notification(CModel):

    MESSAGES = 'ME'
    ACTIVITY = 'AC'
    TYPE_CHOICES = [
        (MESSAGES, 'Messages'),
        (ACTIVITY, 'Activity'),
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

    # ACTIVITY
    activity = models.ForeignKey("activities.Activity", on_delete=models.CASCADE, null=True)

    actor = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
