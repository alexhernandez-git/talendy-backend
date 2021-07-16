from api.utils.models import CModel
from django.contrib.gis.db import models


class Connection(CModel):
    # Login Status
    portal = models.ForeignKey("portals.Portal", on_delete=models.SET_NULL, null=True)
    requester = models.ForeignKey(
        'portals.PortalMember', on_delete=models.CASCADE, related_name='requester')
    addressee = models.ForeignKey(
        'portals.PortalMember', on_delete=models.CASCADE, related_name='addressee')
    accepted = models.BooleanField(default=False)
