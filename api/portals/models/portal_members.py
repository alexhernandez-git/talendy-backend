from api.utils.models import CModel
from django.contrib.gis.db import models

from django.utils.text import slugify


class PortalMember(CModel):

    portal = models.ForeignKey('portals.Portal', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    ADMINISTRATOR = 'AD'
    MANAGER = 'MA'
    BASIC = 'BA'
    MEMBER_TYPE = [
        (ADMINISTRATOR, 'Administrator'),
        (MANAGER, 'Manager'),
        (BASIC, 'Basic'),
    ]

    role = models.CharField(
        max_length=2,
        choices=MEMBER_TYPE,
        default=BASIC
    )
