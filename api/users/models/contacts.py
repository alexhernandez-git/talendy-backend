from api.utils.models import CModel
from django.db import models


class Contact(CModel):
    # Login Status

    from_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="from_contact_user")
    contact_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="to_contact_user")
