from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Models
from api.chats.models import Message, Chat
from api.notifications.models import Notification, NotificationUser
from api.orders.models import Offer

# Utils
from api.utils import helpers
from api.taskapp.tasks import send_activity_notification


@receiver(post_save, sender=Message)
def announce_update_on_messages_model(sender, instance, created, **kwargs):

    chat = instance.chat
    participants = chat.participants.all()
    sent_by = instance.sent_by
    sent_to = participants.exclude(pk=sent_by.pk).first()

    if created:
        # Get or Create the notification user

        if instance.activity:

            notification = Notification.objects.create(
                type=Notification.ACTIVITY,
                activity=instance.activity,
                chat=chat,
                actor=sent_by,
            )
            user_notification = NotificationUser.objects.create(
                notification=notification,
                user=sent_to
            )

            activityModel, _ = helpers.get_activity_classes(instance.activity.type)

            status = ""
            if activityModel:
                activity_queryset = activityModel.objects.filter(activity=instance.activity)
                if activity_queryset.exists():
                    try:
                        activity = activity_queryset.first()
                        # import pdb
                        # pdb.set_trace()
                        status = activity.status
                        # send_activity_notification(activity, instance.activity.type+status)
                    except Exception as e:
                        pass

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "user-%s" % sent_to.id, {
                    "type": "new.activity",
                    "event": instance.activity.type+status,
                    "message": instance,
                    "chat": chat,
                    "sent_by": sent_by,
                    "notification": user_notification,

                }
            )
            async_to_sync(channel_layer.group_send)(
                "user-%s" % sent_by.id, {
                    "type": "new.activity",
                    "event": instance.activity.type+status,
                    "message": instance,
                    "chat": chat,
                    "sent_by": sent_by,
                    "notification": user_notification,

                }
            )
        else:
            # Let celery send have more messages notification
            sent_to.messages_notificatoin_sent = False
            sent_to.save()
            ################################################

            user_notification = NotificationUser.objects.filter(
                user=sent_to,
                is_read=False,
                notification__type=Notification.MESSAGES,
                notification__chat=chat,
                notification__actor=sent_by,
            ).first()

            if not user_notification:

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
                    "notification": user_notification
                }
            )
