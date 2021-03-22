from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import generics
from .serializers import GameBoardSerializer
from .models import GameBoard
from users.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class GameBoardView(generics.RetrieveUpdateAPIView):
    permission_classes = ([IsAuthenticated])
    serializer_class = GameBoardSerializer
    queryset = GameBoard.objects.all()


class NewGameView(generics.CreateAPIView):
    permission_classes = ([IsAuthenticated])
    serializer_class = GameBoardSerializer
    queryset = GameBoard.objects.none()


@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def findGame(request):
    user = request.user
    opponentName = request.data.get("opponent")
    opponent = User.objects.get(username = opponentName)
    if opponent:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        "user%s" % opponent.id,
        {"type": "challenge", "challenger": user.username},
    )
        