import asyncio
from django.core import serializers
from django.http.response import JsonResponse
import json

# Channels
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

# Models
from api.users.models import User


class NoseyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        self.room_group_name = self.room_name
        await self.update_user_status(True)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, message, **kwargs):
        await self.update_user_status(False)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_notification(self, event):

        await self.send_json(event)

    async def message_sent(self, event):

        await self.send_json(event)

    @database_sync_to_async
    def update_user_status(self, is_online):
        return User.objects.filter(id=self.room_name) .update(is_online=is_online)
