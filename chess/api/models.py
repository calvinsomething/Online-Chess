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
    # captured = models.CharField(max_length=29, blank=True)

    
    def makeMove(self, move, playerId):
        legalMoves = self.getMoves(move[0], playerId)
        moveBitset = self.toBitset(move[1], [0, 0])
        print("%%%%%%%%%%M%%%%%%%%%%%%")
        print(legalMoves)
        print(moveBitset)
        print("%%%%%%%%%%M%%%%%%%%%%%%")
        for half in range(2):
            if moveBitset[half] & legalMoves[half]:
                temp = self.alterString(self.board, '0', move[0])
                self.board = self.alterString(temp, self.board[move[0]], move[1])
                self.whitesTurn = not self.whitesTurn
                self.save()
                return True
        return False


    def getMoves(self, piece, playerId):
        playingBlack = playerId == self.blackUser.id
        myPiece = (not playingBlack and self.board[piece] == self.board[piece].lower()) \
            or (playingBlack and self.board[piece] == self.board[piece].upper())
        myTurn = (self.whitesTurn and not playingBlack) \
            or (not self.whitesTurn and playingBlack)
        if myPiece and myTurn:
            return self.movesByPiece[self.board[piece]](self, piece, playingBlack)
        else:
            return [0, 0]
    

    def toBitset(self, square, bitset):
        bitset[square // 32] += 1 << (31 - (square % 32))
        return bitset

    def pawnMoves(self, piece, playingBlack):
        legalMoves = [0, 0]
        if playingBlack:
            if 7 < piece < 16:
                current = piece + 16
                if self.board[current] == '0':
                    legalMoves = self.toBitset(current, legalMoves)
            current = piece + 8
            if self.board[current] == '0':
                legalMoves = self.toBitset(current, legalMoves)
            current = piece + 7
            if self.board[current] != '0' and self.board[current] == self.board[current].lower():
                legalMoves = self.toBitset(current, legalMoves)
            current = piece + 9
            if self.board[current] != '0' and self.board[current] == self.board[current].lower():
                legalMoves = self.toBitset(current, legalMoves)
        else:
            if 47 < piece < 56:
                current = piece - 16
                if self.board[current] == '0':
                    legalMoves = self.toBitset(current, legalMoves)
            current = piece - 8
            if self.board[current] == '0':
                legalMoves = self.toBitset(current, legalMoves)
            current = piece - 7
            if self.board[current] != '0' and self.board[current] == self.board[current].upper():
                legalMoves = self.toBitset(current, legalMoves)
            current = piece - 9
            if self.board[current] != '0' and self.board[current] == self.board[current].upper():
                legalMoves = self.toBitset(current, legalMoves)
        return legalMoves


    def kingMoves(self, piece, playingBlack):
        return self.directions(piece, playingBlack, 'N', 'NW', 'NE', 'W', 'E', 'SW', 'SE', 'S', rng=2)


    def queenMoves(self, piece, playingBlack):
        return self.directions(piece, playingBlack, 'N', 'NW', 'NE', 'W', 'E', 'SW', 'SE', 'S')


    def directions(self, piece, playingBlack, *args, rng=8):
        legalMoves = [0, 0]
        dirs = {
            'N': (-8, lambda sq : sq > -1),
            'NW': (-9, lambda sq : sq > -1 and sq % 8 < 7),
            'NE': (-7, lambda sq : sq > -1 and sq % 8 > 0),
            'W': (-1, lambda sq : sq % 8 < 7),
            'E': (1, lambda sq : sq % 8 > 0),
            'SW': (7, lambda sq : sq < 64 and sq % 8 < 7),
            'SE':(9, lambda sq : sq < 64 and sq % 8 > 0),
            'S': (8, lambda sq : sq < 64)
        }
        checkSquare = lambda pc, direc, dist : pc + direc * dist
        canCapture = lambda inPath : (playingBlack and inPath == inPath.lower()) or (not playingBlack and inPath == inPath.upper())
        
        for arg in args:
            for sq in range(1, rng):
                current = checkSquare(piece, dirs[arg][0], sq)
                if dirs[arg][1](current):
                    if self.board[current] == '0':
                        legalMoves = self.toBitset(current, legalMoves)
                        continue
                    if canCapture(self.board[current]):
                        legalMoves = self.toBitset(current, legalMoves)
                break
        return legalMoves

    def rookMoves(self, piece, playingBlack):
        return self.directions(piece, playingBlack, 'N', 'S', 'W', 'E')


    def knightMoves(self, piece, playingBlack):
        legalMoves = [0, 0]
        positions = []
        dirs = ((-17, lambda sq : sq > -1 and sq % 8 < 7),
            (-15, lambda sq : sq > -1 and sq % 8 > 0),
            (-10, lambda sq : sq > -1 and sq % 8 < 6),
            (-6, lambda sq : sq > -1 and sq % 8 > 1),
            (6, lambda sq : sq < 64 and sq % 8 < 6),
            (10, lambda sq : sq < 64 and sq % 8 > 1),
            (15, lambda sq : sq < 64 and sq % 8 < 7),
            (17, lambda sq : sq < 64 and sq % 8 > 0)
        )
        canCapture = lambda inPath : (playingBlack and inPath == inPath.lower()) or (not playingBlack and inPath == inPath.upper())
        for move in dirs:
            current = piece + move[0]
            if move[1](current) and (self.board[current] == '0' or canCapture(self.board[current])):
                legalMoves = self.toBitset(current, legalMoves)
        return legalMoves


    def bishopMoves(self, piece, playingBlack):
        return self.directions(piece, playingBlack, 'NW', 'NE', 'SW', 'SE')        


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