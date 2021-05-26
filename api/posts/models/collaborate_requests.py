from api.utils.models import CModel
from django.contrib.gis.db import models


class CollaborateRequest(CModel):

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    reason = models.TextField(max_length=300)
