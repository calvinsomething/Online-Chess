import json
from channels.generic.websocket import WebsocketConsumer

class ChessConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        move = text_data_json['move']

        self.send(text_data=json.dumps({
            'move': move
        }))