from api.utils.models import CModel
from django.db import models


class Blacklist(CModel):
    IP = models.GenericIPAddressField()
