from api.utils.models import CModel
from django.db import models


class RequestToContribute(CModel):

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
