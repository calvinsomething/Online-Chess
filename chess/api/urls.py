from django.urls import path
from .views import GameBoardView
# , newGame, findGame

app_name = 'api'

urlpatterns = [
    # path('newgame/', newGame, name='newgame'),
    path('gameboard<int:pk>/', GameBoardView.as_view(), name='gameboard'),
    # path('findgame/', findGame, name='findgame'),
]