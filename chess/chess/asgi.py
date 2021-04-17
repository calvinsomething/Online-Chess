import os
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from . import routing
from .consumers import GameConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chess.settings")

application = ProtocolTypeRouter({
  "http": django_asgi_app,
  "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
    "channel": ChannelNameRouter({
        "thumbnails-generate": consumers.GenerateConsumer.as_asgi(),
        "thumbnails-delete": consumers.DeleteConsumer.as_asgi(),
    }),
})