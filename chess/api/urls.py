from django.urls import path
from .views import GameBoardView, NewGameView


urlpatterns = [
    path('newgame/', NewGameView.as_view(), name='newgame'),
    path('gameboard/', GameBoardView.as_view(), name='gameboard')
]