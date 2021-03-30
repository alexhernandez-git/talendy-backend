from api.utils.models import CModel
from django.db import models


class Offer(CModel):

    send_offer_by_email = models.BooleanField(default=False)
    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="offer_user")
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    karmas_amount = models.IntegerField()


class OfferImage(CModel):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)

    image = models.ImageField(
        'profile picture',
        upload_to='offers/pictures/',
        blank=True,
        null=True,
        max_length=500
    )
    name = models.CharField(max_length=500)

    def save(self, **kwargs):

        try:
            this = OfferImage.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass

        super(OfferImage, self).save(**kwargs)
