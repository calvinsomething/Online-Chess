
from django.contrib import admin
from django.urls import path, include
from .views import home, game

urlpatterns = [
    path('', home, name="home"),
    path('<int:game_id>', game, name="game"),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
    path('rest-auth/', include('rest_auth.urls'))
]
