from api.utils.models import CModel
from django.db import models

# Models
from api.donations.models import DonationOption

# Utils
from django.utils import timezone


class Review(CModel):

    review_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="review_user")
    reviewd_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reviewd_user")
    from_post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)

    rating = models.FloatField(
        null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)
