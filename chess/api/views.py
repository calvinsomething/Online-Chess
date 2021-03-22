from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import generics
from rest_framework.mixins import ListModelMixin
from .serializers import GameBoardSerializer
from .models import GameBoard
from users.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from random import randint
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


class GameBoardView(generics.RetrieveAPIView):
    permission_classes = ([IsAuthenticated])
    serializer_class = GameBoardSerializer
    queryset = GameBoard.objects.all()


@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def newGame(request):
    user = request.user
    opponentName = request.data.get("opponent")
    opponent = User.objects.get(username=opponentName)
    if randint(0,1):
        freshBoard = GameBoard(whiteUserId=user, blackUserId=opponent)
    else:
        freshBoard = GameBoard(whiteUserId=opponent, blackUserId=user)
    freshBoard.save()
    user.currentGame = freshBoard
    user.save()
    opponent.currentGame = freshBoard
    opponent.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
    "user%s" % user.id,
    {"type": "updateBoard", "game_id": freshBoard.id}
    )
    async_to_sync(channel_layer.group_send)(
    "user%s" % opponent.id,
    {"type": "updateBoard", "game_id": freshBoard.id}
    )
    return Response({"new board": freshBoard.id})


@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def findGame(request):
    user = request.user
    opponentName = request.data.get("opponent")
    try:
        opponent = User.objects.get(username = opponentName)
    except:
        return Response({"error": "Can't find that user."})

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
    "user%s" % opponent.id,
    {"type": "incChallenge", "challenger": user.username}
    )

    return Response({"challenging": opponentName})