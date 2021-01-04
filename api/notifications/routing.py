# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r'notifications/', consumers.NoseyConsumer.as_asgi()),
]