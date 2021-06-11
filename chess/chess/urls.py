
from django.contrib import admin
from django.urls import path, include
from .views import home, game
from game_history.views import gameHistory, replay

urlpatterns = [
    path('', home, name="home"),
    path('game_history/', gameHistory, name='game_history'),
    path('replay/<int:game_id>', replay, name='replay'),
    path('<int:game_id>', game, name="game"),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
    path('rest-auth/', include('rest_auth.urls'))
]
