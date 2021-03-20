from rest_framework.decorators import api_view, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import generics
from .serializers import GameBoardSerializer
from .models import GameBoard
from users.models import User

class Test(APIView):

    def get(self, request, *args, **kwargs):
        data = {
            'name': 'John',
            'age': 23
        }
        return Response(data)


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
def findGame(request):
    user = request.user.username
    opponentName = request.data.get("opponent")
    opponent = User.objects.get(username = opponentName)
    if opponent:
        return Response(opponent + user)