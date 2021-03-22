from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<game_id>[1-9]+)/$', consumers.GameConsumer.as_asgi()),
    path('ws/user/', consumers.UserConsumer.as_asgi()),
]