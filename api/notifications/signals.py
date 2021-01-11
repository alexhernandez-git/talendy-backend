from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Models
from api.chats.models import Message, Chat
from api.notifications.models import Notification


@receiver(post_save, sender=Message)
def announce_update_on_messages_model(sender, instance, created, **kwargs):

    chat = instance.chat
    participants = chat.participants.all()
    sent_by = instance.sent_by
    sent_to = participants.exclude(pk=sent_by.pk).first()

    if created:
        # Create the notification

        notification = Notification.objects.create(
            actor=sent_by,
            type=Notification.MESSAGE,
            message=instance,
        )
        # Add the notification to user
        sent_to.notifications.add(notification)
        sent_to.save()

        # Send the event of message to user websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % sent_to.id, {
                "type": "message.sent",
                "event": "New Message",
                "message": instance,
                "chat": chat,
                "sent_by": sent_by,
                "notification": notification
            }
        )
