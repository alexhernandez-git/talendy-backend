from api.utils.models import CModel
from django.db import models


class Message(CModel):
    # Login Status

    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE)
    text = models.TextField(max_length=5000, null=True, blank=True)
    sent_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.ForeignKey("activities.Activity", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["-created"]


class MessageFile(CModel):
    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='messages/files/',
        max_length=500
    )
    name = models.CharField(max_length=500)

    def save(self, **kwargs):

        try:
            this = MessageFile.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete(save=False)
        except:
            pass

        super(MessageFile, self).save(**kwargs)
