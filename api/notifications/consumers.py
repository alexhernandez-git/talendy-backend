import asyncio
from django.core import serializers
from django.http.response import JsonResponse
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json


class NoseyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]

        self.room_group_name = "user-%s" % self.user_id
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, message, **kwargs):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def message_sent(self, event):
        chat = event["chat"]
        message = event["message"]
        sent_by = event["sent_by"]
        notification = event["notification"]

        await self.send_json({
            "event": "MESSAGE_RECEIVED",
            "chat__pk": str(chat.pk),
            "message__pk": str(message.pk),
            "message__text": message.text,
            "message__created": str(message.created),
            "sent_by__pk": str(sent_by.pk),
            "sent_by__username": sent_by.username,
            "notification__pk": str(notification.pk)
        })

    async def new_activity(self, event):
        chat = event["chat"]
        message = event["message"]
        sent_by = event["sent_by"]
        notification = event["notification"]
        event = event["event"]

        await self.send_json({
            "event": event,
            "chat__pk": str(chat.pk),
            "message__pk": str(message.pk),
            "message__text": message.text,
            "message__created": str(message.created),
            "sent_by__pk": str(sent_by.pk),
            "sent_by__username": sent_by.username,
            "notification__pk": str(notification.pk),
        })
