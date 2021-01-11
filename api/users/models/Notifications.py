from api.utils.models import CModel
from django.db import models


class NotificationUser(CModel):
    # Login Status
    notification = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notification_notification')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notification_user')
    is_read = models.BooleanField(default=False)


class Notification(CModel):
    # Login Status

    MESSAGES = 'ME'
    TYPE_CHOICES = [
        (MESSAGES, 'Messages'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )
    message = models.TextField(max_length=5000, null=True, blank=True)
    actor = models.ForeignKey('users.User', on_delete=models.CASCADE)
