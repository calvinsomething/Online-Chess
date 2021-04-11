import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import GameBoard
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class UserConsumer(AsyncWebsocketConsumer):
    game_id = 0
    opponent_id = 0
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
    def getWinner(self, game):
        return game.winner

    @database_sync_to_async
    def myTurn(self):
        game = GameBoard.objects.get(id=self.game_id)
        myTurn = (game.whitesTurn and self.scope['user'].id == game.whiteUser.id)\
            or not (game.whitesTurn or self.scope['user'].id == game.whiteUser.id)
        return myTurn

    @database_sync_to_async
    def getBlackId(self, game):
        return game.blackUser.id

    @database_sync_to_async
    def getMoves(self, piece):
        game = GameBoard.objects.get(id=self.game_id)
        return game.getMoves(piece, self.scope['user'].id)

    @database_sync_to_async
    def choosePromotion(self, promotion, playerId):
        game = GameBoard.objects.get(id=self.game_id)
        if playerId == game.whiteUser.id and 'p' in game.board[:8]:
            game.promote(promotion, playerId)
        elif playerId == game.blackUser.id and 'P' in game.board[56:]:
            game.promote(promotion, playerId)
        async_to_sync(self.updateBoard)()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user%s" % self.opponent_id,
            {"type": "updateBoard"}
        )

    @database_sync_to_async
    def makeMove(self, move):
        game = GameBoard.objects.get(id=self.game_id)
        if game.makeMove(move, self.scope['user'].id):
            async_to_sync(self.updateBoard)()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "user%s" % self.opponent_id,
                {"type": "updateBoard"}
            )

    async def promote(self, event):
        text_data = {
            'promote': 'True'
        }
        await self.send(text_data=json.dumps(text_data))

    async def returnMoves(self, piece):
        moves = await self.getMoves(piece)
        text_data = {
            'moves': moves
        }
        await self.send(text_data=json.dumps(text_data))

    async def updateBoard(self, *args):
        game = await self.getBoard()
        blackId = await self.getBlackId(game)
        winner = await self.getWinner(game)
        data = {
            'board': game.board
        }
        if self.scope['user'].id == blackId:
            data['playingBlack'] = 'True'
        if winner != '0':
            data['winner'] = winner
        elif await self.myTurn():
            data['myTurn'] = 'True'
        await self.send(text_data=json.dumps(data))

    async def newGame(self, event):
        self.game_id = event['game_id']
        self.opponent_id = event['opponent_id']
        await self.updateBoard()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('getMoves'):
            await self.returnMoves(text_data_json['getMoves'] - 1)
        if text_data_json.get('makeMove'):
            await self.makeMove(text_data_json['makeMove'])
        if text_data_json.get('promotion'):
            await self.choosePromotion(text_data_json['promotion'], self.scope['user'].id)

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