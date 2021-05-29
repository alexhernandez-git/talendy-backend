from api.utils.models import CModel
from django.contrib.gis.db import models


class KanbanList(CModel):
    post = models.ForeignKey("posts.KanbanList", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField()


class KanbanCard(CModel):
    list = models.ForeignKey("posts.KanbanCard", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.IntegerField()

    class Meta:
        """Meta option."""

        ordering = ['order']
