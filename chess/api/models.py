from django.db import models
from django.utils import timezone
from random import randint

# Create your models here.

class SavedGame(models.Model):
    whiteUserId = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='whiteUserId')
    blackUserId = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='blackUserId')
    date_played = models.DateTimeField(default=timezone.now)
    moves = models.TextField()

    def __str__(self):
        return self.title

class GameBoard(models.Model):
    def flipCoin():
        return randint(0,1)


    whitesTurn = models.BooleanField(default=flipCoin)
    board = models.CharField(max_length=64, default="\
        RNBQKBNR\
        PPPPPPPP\
        00000000\
        00000000\
        00000000\
        00000000\
        pppppppp\
        rnbqkbnr")
    