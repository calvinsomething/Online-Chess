from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import generics
from .serializers import GameBoardSerializer
from .models import GameBoard

# Create your views here.
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