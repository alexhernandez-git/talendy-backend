from api.utils.models import CModel
from django.contrib.gis.db import models


class PostSeenBy(CModel):
    # Login Status

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="seen_by_post")

    message = models.ForeignKey(
        "posts.PostMessage", on_delete=models.CASCADE, null=True, related_name="seen_by_post_message"
    )

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="seen_by_post_user")
