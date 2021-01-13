from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Models
from api.chats.models import Message, Chat
from api.notifications.models import Notification, NotificationUser


@receiver(post_save, sender=Message)
def announce_update_on_messages_model(sender, instance, created, **kwargs):

    chat = instance.chat
    participants = chat.participants.all()
    sent_by = instance.sent_by
    sent_to = participants.exclude(pk=sent_by.pk).first()

    if created:
        # Get or Create the notification user

        user_notification = None
        try:
            user_notification = NotificationUser.objects.get(
                user=sent_to,
                is_read=False,
                notification__type=Notification.MESSAGES,
                notification__chat=chat,
                notification__actor=sent_by,
            )
        except NotificationUser.DoesNotExist:

            notification = Notification.objects.create(
                type=Notification.MESSAGES,
                chat=chat,
                actor=sent_by,
            )

            user_notification = NotificationUser.objects.create(
                notification=notification,
                user=sent_to
            )

        user_notification.notification.messages.add(instance)
        user_notification.notification.save()

        # Send the event of message to user websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user-%s" % sent_to.id, {
                "type": "message.sent",
                "event": "New Message",
                "message": instance,
                "chat": chat,
                "sent_by": sent_by,
                "notification": user_notification.notification
            }
        )
