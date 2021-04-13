from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from api.notifications import routing as notifications_routing

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                notifications_routing.websocket_urlpatterns
            )
        ),
    }
)
