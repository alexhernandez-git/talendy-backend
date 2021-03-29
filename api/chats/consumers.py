# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .views.messages import create_message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        files = text_data_json['files']

        text = text_data_json["text"]
        sent_by = text_data_json["sent_by"]
        # Send message to room group

        # Create message

        message, chat__pk, files = await create_message(self, text, sent_by, files)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": str(message.id),
                "text": text,
                "sent_by": sent_by,
                "created": str(message.created),
                "chat__pk": str(chat__pk),
                "files": files
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        id = event["id"]
        text = event["text"]
        sent_by = event["sent_by"]
        created = event["created"]
        chat__pk = event["chat__pk"]
        files = event["files"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({
                "id": id,
                "text": text,
                "sent_by": sent_by,
                "created": created,
                "chat__id": chat__pk,
                "files": files,
            })
        )
