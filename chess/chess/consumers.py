import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import GameBoard

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "user%s" % self.scope['user'].id
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        
    async def challenge(self, event):
        challenger = event['challenger']

        await self.send(text_data=json.dumps({
            'challenger': challenger
        }))

    async def receive(self, text_data):
        pass

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_id,
            self.channel_name
        )

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_id = 'game_%s' % self.game_id
        self.player = self.scope['user']

        board = GameBoard.objects.create(whiteUserId = whiteID, blackUserId = blackID)
        # Join room group
        await self.channel_layer.group_add(
            self.game_group_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_id,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        board = text_data_json['board']
        

        # Send move to game group
        await self.channel_layer.group_send(
            self.game_group_id,
            {
                'type': 'board_update',
                'board': board,
            }
        )

    # Receive board update from game group
    async def board_update(self, event):
        board = event['board']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'board': board
        }))