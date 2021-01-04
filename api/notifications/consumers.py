import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NoseyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("user-1", self.channel_name)
        print(f"Added {self.channel_name} channel to gossip")
    
    async def disconnect(self, message, **kwargs):
        await self.channel_layer.group_discard("user-1", self.channel_name)
        print(f"Removed {self.channel_name} channel to gossip")

    async def user_gossip(self,event):
        await self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")

    async def user_update(self,event):
        await self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")