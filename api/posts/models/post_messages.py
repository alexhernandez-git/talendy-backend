from api.utils.models import CModel
from django.contrib.gis.db import models


class PostMessage(CModel):
    # Login Status

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    text = models.TextField(max_length=5000, null=True, blank=True)
    sent_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-created"]


class PostMessageFile(CModel):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(PostMessage, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='post/messages/files/',
        max_length=500
    )
    name = models.CharField(max_length=500)

    def save(self, **kwargs):

        try:
            this = PostMessageFile.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete(save=False)
        except:
            pass

        super(PostMessageFile, self).save(**kwargs)
