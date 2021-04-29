from api.utils.models import CModel
from django.db import models


class PostMember(CModel):

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    BASIC = 'BA'
    ADMIN = 'AD'
    ROLE_TYPES = [
        (BASIC, 'Basic'),
        (ADMIN, 'Admin'),
    ]

    role = models.CharField(
        max_length=2,
        choices=ROLE_TYPES,
        default=BASIC
    )
