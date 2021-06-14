from api.utils.models import CModel
from django.contrib.gis.db import models

from django.utils.text import slugify


class Portal(CModel):

    name = models.CharField('Portal name', max_length=140)

    url = models.SlugField(max_length=40)

    users = models.ManyToManyField(
        "users.User", through="portals.PortalMember", verbose_name="room_participants"
    )

    owner = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="portal_owner")

    about = models.TextField('about client', max_length=500, null=True, blank=True)

    logo = models.ImageField(
        'client logo',
        upload_to='portals/logos/',
        blank=True,
        null=True,
        max_length=500
    )

    # Config
    donations_enabled = models.BooleanField(default=False)

    # Users count
    all_users_count = models.IntegerField(default=0)

    admins_count = models.IntegerField(default=0)

    managers_count = models.IntegerField(default=0)

    users_count = models.IntegerField(default=0)

    posts_count = models.IntegerField(default=0)

    created_posts_count = models.IntegerField(default=0)

    created_active_posts_count = models.IntegerField(default=0)

    created_solved_posts_count = models.IntegerField(default=0)

    collaborated_posts_count = models.IntegerField(default=0)

    collaborated_active_posts_count = models.IntegerField(default=0)

    collaborated_solved_posts_count = models.IntegerField(default=0)
