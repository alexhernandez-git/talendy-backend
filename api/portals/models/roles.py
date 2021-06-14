from api.utils.models import CModel
from django.contrib.gis.db import models

from django.utils.text import slugify


class Role(CModel):

    name = models.CharField('Role name', max_length=140)

    ADMINISTRATOR = 'AD'
    MANAGERS = 'MA'
    BASIC = 'BA'

    ROLE_CHOICES = [
        (ADMINISTRATOR, 'Administrator'),
        (MANAGERS, 'Managers'),
        (BASIC, 'Basic'),
    ]

    role = models.CharField(
        max_length=2,
        choices=ROLE_CHOICES,
    )

    portal = models.ForeignKey('portals.Portal', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
