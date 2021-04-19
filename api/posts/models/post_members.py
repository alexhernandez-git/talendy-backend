from api.utils.models import CModel
from django.db import models


class PostMember(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
