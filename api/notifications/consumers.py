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
        chat = serializers.serialize('json', [event["chat"]])
        message = serializers.serialize('json', [event["message"]])

        await self.send_json({"chat": chat, "message": message})
