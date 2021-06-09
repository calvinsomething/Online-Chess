from django.contrib import admin
from .models import GameBoard

class GameBoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'moves')

admin.site.register(GameBoard, GameBoardAdmin)
