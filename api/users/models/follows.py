from api.utils.models import CModel
from django.contrib.gis.db import models


class Follow(CModel):
    # Login Status
    portal = models.ForeignKey("portals.Portal", on_delete=models.SET_NULL, null=True)

    from_member = models.ForeignKey('portals.PortalMember', on_delete=models.CASCADE, related_name="from_follow_member")
    followed_member = models.ForeignKey(
        'portals.PortalMember', on_delete=models.CASCADE, related_name="to_followed_member")
