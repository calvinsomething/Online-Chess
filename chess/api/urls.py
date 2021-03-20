from django.urls import path
from .views import GameBoardView, NewGameView, Test, findGame

app_name = 'api'

urlpatterns = [
    path('newgame/', NewGameView.as_view(), name='newgame'),
    path('gameboard/', GameBoardView.as_view(), name='gameboard'),
    path('findgame/', findGame, name='findgame'),
    path('test/', Test.as_view(), name='test')
]