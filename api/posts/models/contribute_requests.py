from api.utils.models import CModel
from django.db import models


class ContributeRequest(CModel):

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    reason = models.TextField(max_length=300)
    is_accepted = models.BooleanField(default=False)
