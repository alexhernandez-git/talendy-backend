from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from api.chat import routing as chat_routing
from api.notifications import routing as notifications_routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter( 
            chat_routing.websocket_urlpatterns +
            notifications_routing.websocket_urlpatterns
        )
    ),
})