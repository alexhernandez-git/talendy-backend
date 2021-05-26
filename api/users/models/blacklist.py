from api.utils.models import CModel
from django.contrib.gis.db import models


class Blacklist(CModel):
    IP = models.GenericIPAddressField()
