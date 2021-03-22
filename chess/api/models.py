from django.db import models
from django.utils import timezone
from random import randint


class GameBoard(models.Model):
    def flipCoin():
        return randint(0,1)
    
    whiteUserId = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='whiteUserId')
    blackUserId = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='blackUserId')
    timeStarted = models.DateTimeField(default=timezone.now)
    whitesTurn = models.BooleanField(default=True)
    board = models.CharField(max_length=64, default="\
        RNBQKBNR\
        PPPPPPPP\
        00000000\
        00000000\
        00000000\
        00000000\
        pppppppp\
        rnbqkbnr")
    
    moves = models.TextField()