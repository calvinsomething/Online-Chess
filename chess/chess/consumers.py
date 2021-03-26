import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import GameBoard
from channels.db import database_sync_to_async

class UserConsumer(AsyncWebsocketConsumer):
    game_id = 0
    async def connect(self):
        self.group_name = "user%s" % self.scope['user'].id
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def incChallenge(self, event):
        challenger = event['challenger']

        await self.send(text_data=json.dumps({
            'challenger': challenger
        }))

    @database_sync_to_async
    def getBoard(self):
        return GameBoard.objects.get(id=self.game_id)

    @database_sync_to_async
    def getBlackId(self, game):
        return game.blackUser.id

    @database_sync_to_async
    def getMoves(self, piece):
        game = GameBoard.objects.get(id=self.game_id)
        return game.getMoves(piece, self.scope['user'].id)

    async def returnMoves(self, piece):
        moves = await self.getMoves(piece)
        text_data = {
            'moves': moves
        }
        await self.send(text_data=json.dumps(text_data))

    async def updateBoard(self, event):
        self.game_id = event['game_id']
        game = await self.getBoard()
        blackId = await self.getBlackId(game)
        data = {
            'user': blackId,
            'board': game.board
        }
        if self.scope['user'].id == blackId:
            data['playingBlack'] = 'True'
        else:
            board = game.board
        await self.send(text_data=json.dumps(data))

    async def newGame(self, event):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['getMoves']:
            await self.returnMoves(text_data_json['getMoves'])

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
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