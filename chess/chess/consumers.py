import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_id = 'game_%s' % self.game_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_id,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_id,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        board = text_data_json['board']

        # Send move to game group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_id,
            {
                'type': 'board_update',
                'board': board
            }
        )

    # Receive board update from game group
    def board_update(self, event):
        board = event['board']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'board': board
        }))