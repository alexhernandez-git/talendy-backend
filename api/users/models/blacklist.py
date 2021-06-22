from api.utils.models import CModel
from django.contrib.gis.db import models


class Blacklist(CModel):
    portal = models.ForeignKey("portals.Portal", on_delete=models.SET_NULL, null=True)
    IP = models.GenericIPAddressField()
