from api.utils.models import CModel
from django.contrib.gis.db import models


class Community(CModel):

    name = models.CharField(max_length=100)
