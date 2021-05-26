from api.utils.models import CModel
from django.contrib.gis.db import models


class Follow(CModel):
    # Login Status

    from_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="from_follow_user")
    followed_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="to_followed_user")
