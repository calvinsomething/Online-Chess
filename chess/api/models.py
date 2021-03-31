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

    
    def makeMove(self, move, playerId):
        legalMoves = self.getMoves(move[0], playerId)
        row = move[1] // 8
        col = move[1] % 8
        if legalMoves[row] & (1 << (7 - col)):
            temp = self.alterString(self.board, '0', move[0])
            self.board = self.alterString(temp, self.board[move[0]], move[1])
            self.whitesTurn = not self.whitesTurn
            self.save()
            return True
        return False


    def getMoves(self, piece, playerId):
        myPiece = (playerId == self.whiteUser.id and self.board[piece] == self.board[piece].lower()) \
            or (playerId == self.blackUser.id and self.board[piece] == self.board[piece].upper())
        myTurn = (self.whitesTurn and playerId == self.whiteUser.id) \
            or not (self.whitesTurn or playerId == self.whiteUser.id)
        if myPiece and myTurn:
            return self.movesByPiece[self.board[piece]](self, piece)
        else:
            return [0 for row in range(8)]
        

    def pawnMoves(self, piece):
        legalMoves = [0 for row in range(8)]
        col = piece % 8
        row = piece // 8
        if self.board[piece] == 'p':
            if self.board[piece - 8] == '0':
                legalMoves[row - 1] = 1 << (7 - col)
            else: return legalMoves
            if row == 6 and self.board[piece - 16] == '0':
                    legalMoves[4] = 1 << (7 - col)
        else:
            if self.board[piece + 8] == '0':
                legalMoves[row + 1] = 1 << (7 - col)
            else: return legalMoves
            if row == 1 and self.board[piece + 16] == '0':
                    legalMoves[3] = 1 << (7 - col)
        return legalMoves


    def kingMoves(self, piece):
        return self.queenMoves(piece, isKing = True)


    def queenMoves(self, piece, isKing = False):
        legalMoves = '0' * 64
        row = piece // 8
        col = piece % 8
        positions = []
        if isKing:
            rng = 1
        else:
            if 7 - row > row:
                rng = 8 - row
            else:
                rng = row + 1
            if (7 - col > col) and (7 - col > rng):
                rng = 8 - col
            elif col > rng:
                rng = col + 1
        moves = (1, 7, 8, 9)
        for dist in range(rng):
            for move in moves:
                if move * rng < 64:
                    positions.append(move * rng)
                if -(move * rng) > -1:
                    positions.append(-(move * rng))
        positions.sort()
        return self.alterString(legalMoves, '1', *positions)


    def rookMoves(self, piece):
        legalMoves = '0' * 64
        row = piece // 8
        col = piece % 8
        positions = []
        playingBlack = self.board[piece] == self.board[piece].upper()

        #up down left right
        v1, v2, h1, h2 = True, True, True, True
        for sq in range(7):
            if v1:
                if row - sq > -1:
                    pass


        for sq in range(8):
            if sq != row:
                playingBlack = self.board[piece] == self.board[piece].upper()
                positions.append(sq * 8 + col)
            if sq != col:
                positions.append(row * 8 + sq)
        positions.sort()
        return self.alterString(legalMoves, '1', *positions)


    def knightMoves(self, piece):
        legalMoves = '0' * 64
        positions = []
        moves = (6, 10, 15, 17)
        for move in moves:
            if piece - move > -1:
                positions.append(piece - move)
            if piece + move < 64:
                positions.append(piece + move)
        positions.sort()
        return self.alterString(legalMoves, '1', *positions)

    def bishopMoves(self, piece):
        legalMoves = '0' * 64
        row = piece // 8
        col = piece % 8
        positions = []
        diff = 1
        while (row - diff > -1) or (row + diff < 8):
            current = row - diff
            if current > -1:
                positions.append(current - diff)
                positions.append(current + diff)
            current = row + diff
            if current < 8:
                positions.append(current - diff)
                positions.append(current + diff)
        positions.sort()
        return self.alterString(legalMoves, '1', *positions)

    def alterString(self, string, value, *positions):
        segments = []
        lastPos = 0
        for position in positions:
            if 0 > position > 63:
                continue
            segments.append(string[lastPos:position] + value)
            lastPos = position + 1
        segments.append(string[lastPos:])
        newString = ''
        for segment in segments:
            newString += segment
        return newString

    
    movesByPiece = {
        'p': pawnMoves,
        'P': pawnMoves,
        'r': rookMoves,
        'R': rookMoves,
        'n': knightMoves,
        'N': knightMoves,
        'b': bishopMoves,
        'B': bishopMoves,
        'q': queenMoves,
        'Q': queenMoves,
        'k': kingMoves,
        'K': kingMoves
    }