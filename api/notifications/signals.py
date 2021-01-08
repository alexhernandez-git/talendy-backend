from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Models
from api.chats.models import Message, Chat


@receiver(post_save, sender=Message)
def announce_update_on_messages_model(sender, instance, created, **kwargs):

    chat = instance.chat
    participants = chat.participants.all()
    sent_by = instance.sent_by
    sent_to = participants.exclude(pk=sent_by.pk).first()

    if created:

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % sent_to.id, {
                "type": "message.sent",
                "event": "New Message",
                "message": instance,
                "chat": chat
            }
        )
