from api.utils.models import CModel
from django.contrib.gis.db import models

from django.utils.text import slugify


class Client(CModel):

    name = models.CharField('Client name', max_length=140)
    slug_name = models.SlugField(max_length=40)
    users = models.ManyToManyField(
        "users.User", through="clients.Role", verbose_name="room_participants"
    )

    # Config
    donations_enabled = models.BooleanField(default=False)
