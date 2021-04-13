from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Models
from api.chats.models import Message, Chat
from api.notifications.models import Notification, NotificationUser

# Utils
from api.utils import helpers
from api.taskapp.tasks import send_have_messages_from_email


@receiver(post_save, sender=Message)
def announce_update_on_messages_model(sender, instance, created, **kwargs):

    chat = instance.chat
    participants = chat.participants.all()
    sent_by = instance.sent_by
    sent_to = participants.exclude(pk=sent_by.pk).first()

    if created:
        # Get or Create the notification user

        user_notification = NotificationUser.objects.filter(
            user=sent_to,
            is_read=False,
            notification__type=Notification.MESSAGES,
            notification__chat=chat,
            notification__actor=sent_by,
        ).first()

        if not user_notification:
            # Insert here the send new message email notification
            if not sent_to.is_online:
                async_to_sync(send_have_messages_from_email(sent_to, sent_by))
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
                "event": "MESSAGE_RECEIVED",
                "type": "new.activity",
                "chat__pk": str(chat.pk),
                "message__pk": str(instance.pk),
                "message__text": instance.text,
                "message__created": str(instance.created),
                "sent_by__pk": str(sent_by.pk),
                "sent_by__username": sent_by.username,
                "notification__pk": str(user_notification.pk),
            }
        )
