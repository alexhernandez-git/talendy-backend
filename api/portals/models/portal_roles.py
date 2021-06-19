from api.utils.models import CModel
from django.contrib.gis.db import models

from django.utils.text import slugify


class PortalRole(CModel):

    code = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True, null=True)
