from api.utils.models import CModel
from django.db import models


class Oportunity(CModel):

    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="oportunity_user")
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    karmas_amount = models.IntegerField()


class OportunityImage(CModel):
    oportunity = models.ForeignKey(Oportunity, on_delete=models.CASCADE)

    image = models.ImageField(
        'profile picture',
        upload_to='oportunities/pictures/',
        blank=True,
        null=True,
        max_length=500
    )
    name = models.CharField(max_length=500)

    def save(self, **kwargs):

        try:
            this = OportunityImage.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass

        super(OportunityImage, self).save(**kwargs)
