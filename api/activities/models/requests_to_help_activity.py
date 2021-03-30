from api.utils.models import CModel
from django.db import models


class RevisionActivity(CModel):

    activity = models.OneToOneField(
        "activities.Activity", on_delete=models.CASCADE, null=True
    )

    request_to_help = models.ForeignKey(
        "orders.RequestToHelp", on_delete=models.CASCADE
    )
