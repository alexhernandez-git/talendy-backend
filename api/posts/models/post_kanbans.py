from api.utils.models import CModel
from django.contrib.gis.db import models

import uuid


class KanbanList(CModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField()

    class Meta:
        """Meta option."""

        ordering = ['order']


class KanbanCard(CModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)

    kanban_list = models.ForeignKey("posts.KanbanList", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.IntegerField()

    class Meta:
        """Meta option."""

        ordering = ['order']
