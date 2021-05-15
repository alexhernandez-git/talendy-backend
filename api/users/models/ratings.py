from api.utils.models import CModel
from django.db import models

# Models
from api.donations.models import DonationItem

# Utils
from django.utils import timezone


class Rating(CModel):

    rating_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="rating_user")
    rated_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="rated_user")
    from_post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)

    rating = models.FloatField(
        null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)
