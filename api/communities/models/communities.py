from api.utils.models import CModel
from django.db import models


class Community(CModel):

    name = models.CharField(max_length=100)
