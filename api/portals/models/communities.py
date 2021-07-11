from api.utils.models import CModel
from django.contrib.gis.db import models


class Community(CModel):
    portal = models.ForeignKey("portals.Portal", on_delete=models.CASCADE, related_name="community_portal")

    name = models.CharField(max_length=100)

    posts_count = models.IntegerField(default=0)

    created_posts_count = models.IntegerField(default=0)

    created_active_posts_count = models.IntegerField(default=0)

    created_solved_posts_count = models.IntegerField(default=0)

    collaborated_posts_count = models.IntegerField(default=0)

    collaborated_active_posts_count = models.IntegerField(default=0)

    collaborated_solved_posts_count = models.IntegerField(default=0)
