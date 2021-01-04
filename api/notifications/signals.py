from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=User)
def announce_update_on_users_model(sender, instance, created, **kwargs):
    if(instance.email == 'alex@gmail.com'):
        if created:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "user-{}".format(instance.id),{
                    "type":"user.gossip",
                    "event": "New User",
                    "username": instance.username
                }
            )
        if not created:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "user-{}".format(instance.id),{
                    "type":"user.update",
                    "event": "User Update",
                    "username": instance.username,
                }
            )