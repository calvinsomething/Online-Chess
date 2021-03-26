from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class GameBoard(models.Model):
    whiteUser = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='whiteUser')
    blackUser = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='blackUser')
    timeStarted = models.DateTimeField(default=timezone.now)
    whitesTurn = models.BooleanField(default=True)
    checkMate = models.BooleanField(default=False)
    board = models.CharField(max_length=64, default=\
        "RNBQKBNR" + \
        "PPPPPPPP" + \
        "00000000" + \
        "00000000" + \
        "00000000" + \
        "00000000" + \
        "pppppppp" + \
        "rnbqkbnr")
    
    moves = models.TextField(blank=True)

    def getMoves(self, piece, playerId):
        legalMoves = '0' * 64
        if self.board[piece] == 'p':
            if 47 < piece < 56:
                legalMoves = self.alterString(legalMoves, '1', piece - 16, piece - 8)
            else:
                legalMoves = self.alterString(legalMoves, '1', piece - 8)
        return legalMoves

    
    def alterString(self, string, value, *positions):
        segments = []
        lastPos = 0
        for position in positions:
            segments.append(string[lastPos:position] + value)
            lastPos = position + 1
        segments.append(string[lastPos:])
        newString = ''
        for segment in segments:
            newString += segment
        return newString