from api.utils.models import CModel
from django.db import models


class NotificationUser(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class Notification(CModel):

    MESSAGE = 'ME'
    TYPE_CHOICES = [
        (MESSAGE, 'Message'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )
    message = models.ForeignKey(
        "chats.Message", on_delete=models.CASCADE, null=True, related_name="notifications_message"
    )
    actor = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
