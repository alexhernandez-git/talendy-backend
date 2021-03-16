from api.utils.models import CModel
from django.db import models


class SeenBy(CModel):
    # Login Status

    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE, related_name="seen_by_chat")

    message = models.ForeignKey(
        "chats.Message", on_delete=models.CASCADE, null=True, related_name="seen_by_message"
    )

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="seen_by_user")
