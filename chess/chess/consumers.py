import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer
from api.models import GameBoard
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from users.models import User
from random import randint
from pathlib import Path

class GameConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.send({
            "type": "websocket.accept",
        })

    def websocket_receive(self, event):
        self.send({
            "type": "websocket.send",
            "text": event["text"],
        })

    def findGame(self, event):
        user = self.scope['user']
        print('FINDING GAME.....')
        print(self.channel_name)
        try:
            opponent = User.objects.get(username=opponentName)
        except:
            return #Response({"error": "Can't find that user."})
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        "user%s" % opponent.id,
        {"type": "incChallenge", "challenger": user.username}
        )
        print('Challenge sent to ' + opponentName)

    def startGame(self, event):
        print("STARTING GAME....")
        user = User.objects.get(id=event['user_id'])
        opponent = User.objects.get(username=event['opponentName'])
        if randint(0,1):
            freshBoard = GameBoard(whiteUser=user, blackUser=opponent)
        else:
            freshBoard = GameBoard(whiteUser=opponent, blackUser=user)
        freshBoard.save()
        user.currentGame = freshBoard
        user.save()
        opponent.currentGame = freshBoard
        opponent.save()
        self.updateBoard(user, opponent, freshBoard)

    def choosePromotion(self, event):
        user = User.objects.get(id=event['user_id'])
        game = user.currentGame
        if user.id == game.whiteUser.id and 'p' in game.board[:8]:
            game.promote(event['promotion'], user.id)
            opponent = game.blackUser
        elif user.id == game.blackUser.id and 'P' in game.board[56:]:
            game.promote(event['promotion'], user.id)
            opponent = game.whiteUser
        self.updateBoard(user, opponent, game)

    def updateBoard(self, user, opponent, game):
        for player in (user, opponent):
            playingBlack = player == game.blackUser
            myTurn = (game.whitesTurn and not playingBlack)\
                or (not game.whitesTurn and playingBlack)
            text_data = {
                'board': game.board,
                'captured': game.captured
            }
            if playingBlack:
                text_data['playingBlack'] = 'True'
            if game.winner != '0':
                text_data['winner'] = game.winner
            elif myTurn:
                text_data['myTurn'] = 'True'
            async_to_sync(self.channel_layer.group_send)(
                "user%s" % player.id,
                {"type": "updateClient", "json_data": json.dumps(text_data)}
            )

    def getMoves(self, event):
        user = User.objects.get(id=event['user_id'])
        text_data = {
            'moves': user.currentGame.getMoves(event['piece'], event['user_id'])
        }
        async_to_sync(self.channel_layer.group_send)(
            "user%s" % event['user_id'],
            {"type": "updateClient", "json_data": json.dumps(text_data)}
        )

    def makeMove(self, event):
        user = User.objects.get(id=event['user_id'])
        game = user.currentGame
        if game.makeMove(event['move'], event['user_id']):
            self.updateBoard(game.whiteUser, game.blackUser, game)


class UserConsumer(AsyncWebsocketConsumer):
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

    async def startGame(self, opponentName):
        await self.channel_layer.send(
        "game",
        {"type": "startGame", "user_id": self.scope['user'].id, "opponentName": opponentName}
        )

    @database_sync_to_async
    def findGame(self, opponentName):
        user = self.scope['user']
        print('FINDING GAME.....')
        print(self.channel_name)
        try:
            opponent = User.objects.get(username__iexact=opponentName)
        except:
            return #Response({"error": "Can't find that user."})
        async_to_sync(self.channel_layer.group_send)(
        "user%s" % opponent.id,
        {"type": "incChallenge", "challenger": user.username}
        )
        print('Challenge sent to ' + opponentName)


    # @database_sync_to_async
    # def getBoard(self):
    #     return GameBoard.objects.get(id=self.game_id)

    # @database_sync_to_async
    # def getWinner(self, game):
    #     return game.winner

    # @database_sync_to_async
    # def myTurn(self):
    #     game = GameBoard.objects.get(id=self.game_id)
    #     myTurn = (game.whitesTurn and self.scope['user'].id == game.whiteUser.id)\
    #         or not (game.whitesTurn or self.scope['user'].id == game.whiteUser.id)
    #     return myTurn

    # @database_sync_to_async
    # def getBlackId(self, game):
    #     return game.blackUser.id

    async def getMoves(self, piece):
        await self.channel_layer.send(
            "game",
            {"type": "getMoves", "piece": piece, "user_id": self.scope['user'].id}
        )

    # @database_sync_to_async
    # def choosePromotion(self, promotion, playerId):
    #     game = GameBoard.objects.get(id=0)
    #     if playerId == game.whiteUser.id and 'p' in game.board[:8]:
    #         game.promote(promotion, playerId)
    #     elif playerId == game.blackUser.id and 'P' in game.board[56:]:
    #         game.promote(promotion, playerId)
    #     async_to_sync(self.updateBoard)()
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         "user%s" % self.opponent_id,
    #         {"type": "updateBoard"}
    #     )

    async def makeMove(self, move):
        await self.channel_layer.send(
            "game",
            {"type": "makeMove", "move": move, "user_id": self.scope['user'].id}
        )

    async def choosePromotion(self, promotion):
        await self.channel_layer.send(
            "game",
            {"type": "choosePromotion", "promotion": promotion, "user_id": self.scope['user'].id}
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

    async def updateClient(self, event):
        await self.send(text_data=event['json_data'])

    # async def newGame(self, event):
    #     self.game_id = event['game_id']
    #     self.opponent_id = event['opponent_id']
    #     await self.updateBoard()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('getMoves'):
            await self.getMoves(text_data_json['getMoves'] - 1)
        if text_data_json.get('makeMove'):
            await self.makeMove(text_data_json['makeMove'])
        if text_data_json.get('promotion'):
            await self.choosePromotion(text_data_json['promotion'])
        if text_data_json.get('gameVS'):
            await self.startGame(text_data_json['gameVS'])
        if text_data_json.get('challenge'):
            await self.findGame(text_data_json['challenge'])

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


# class GameConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.game_id = self.scope['url_route']['kwargs']['game_id']
#         self.game_group_id = 'game_%s' % self.game_id
#         self.player = self.scope['user']

#         board = GameBoard.objects.create(whiteUserId = whiteID, blackUserId = blackID)
#         # Join room group
#         await self.channel_layer.group_add(
#             self.game_group_id,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave game group
#         await self.channel_layer.group_discard(
#             self.game_group_id,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         board = text_data_json['board']

#         # Send move to game group
#         await self.channel_layer.group_send(
#             self.game_group_id,
#             {
#                 'type': 'board_update',
#                 'board': board,
#             }
#         )

#     # Receive board update from game group
#     async def board_update(self, event):
#         board = event['board']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'board': board
#         }))