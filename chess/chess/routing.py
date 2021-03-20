from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    #re_path(r'ws/moves/(?P<game_id>\w+)/$', consumers.ChessConsumer.as_asgi()),
    re_path(r'ws/moves/', consumers.ChessConsumer.as_asgi()),
]