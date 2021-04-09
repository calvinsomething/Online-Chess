from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class GameBoard(models.Model):
    whiteUser = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='whiteUser')
    blackUser = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='blackUser')
    timeStarted = models.DateTimeField(default=timezone.now)
    whitesTurn = models.BooleanField(default=True)
    check = models.BooleanField(default=False)
    winner = models.CharField(max_length=1, default=0)
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
    enPassant = models.IntegerField(default=-1)
    castle = models.IntegerField(default=15)
    captured = models.CharField(max_length=30, blank=True)
    wAttacksTop = models.IntegerField(default=0)
    wAttacksBottom = models.IntegerField(default=0)
    bAttacksTop = models.IntegerField(default=0)
    bAttacksBottom = models.IntegerField(default=0)
    kAttacker1 = models.IntegerField(default=-1)
    kAttacker2 = models.IntegerField(default=-1)


    def setAttacks(self):
        wAttacks = [0, 0]
        bAttacks = [0, 0]
        self.kAttacker1, self.kAttacker2 = -1, -1
        for sq in range(64):
            if self.board[sq] == '0': continue
            playingBlack = self.board[sq] == self.board[sq].upper()
            attacks = self.movesByPiece[self.board[sq]](self, sq, playingBlack, attacks=True)
            if self.board[sq] == self.board[sq].lower():
                for half in range(2):
                    wAttacks[half] += attacks[half] - (wAttacks[half] & attacks[half])
            else:
                for half in range(2):
                    bAttacks[half] += attacks[half] - (wAttacks[half] & attacks[half])
        self.wAttacksTop = wAttacks[0]
        self.wAttacksBottom = wAttacks[1]
        self.bAttacksTop = bAttacks[0]
        self.bAttacksBottom = bAttacks[1]


    def makeMove(self, move, playerId):
        legalMoves = self.getMoves(move[0], playerId)
        moveBitset = self.toBitset(move[1], [0, 0])
        for half in range(2):
            if moveBitset[half] & legalMoves[half]:
                if move[1] == self.enPassant and self.board[move[0]].upper() == 'P':
                    self.alterBoard(move[1], move[0] + (move[1] % 8 - move[0] % 8))
                if move[1] - move[0] == 16 and self.board[move[0]] == 'P': self.enPassant = move[0] + 8
                elif move[0] - move[1] == 16 and self.board[move[0]] == 'p': self.enPassant = move[0] - 8
                else: self.enPassant = -1
                self.alterBoard(move[0], move[1])
                self.setAttacks()
                self.whitesTurn = not self.whitesTurn
                self.isGameOver(playerId)
                self.save()
                return True
        return False


    def isGameOver(self, playerId):
        if playerId == self.blackUser.id:
            playingBlack = True
            opponentId = self.whiteUser.id
        else:
            playingBlack = False
            opponentId = self.blackUser.id
        for sq in range(64):
            if self.board[sq] == '0': continue
            if (self.board[sq] == self.board[sq].upper()) != playingBlack:
                if self.getMoves(sq, opponentId) != [0, 0]:
                    return
        if not self.check:
            self.winner = 'D'
        elif playingBlack:
            self.winner = 'B'
        else:
            self.winner = 'W'


    def getMoves(self, piece, playerId):
        playingBlack = playerId == self.blackUser.id
        myPiece = (not playingBlack and self.board[piece] == self.board[piece].lower()) \
            or (playingBlack and self.board[piece] == self.board[piece].upper())
        myTurn = (self.whitesTurn and not playingBlack) \
            or (not self.whitesTurn and playingBlack)
        if myPiece and myTurn:
            return [self.protectingKing(piece, playingBlack)[half] \
                & self.movesByPiece[self.board[piece]](self, piece, playingBlack)[half] \
                & self.inCheck(piece, playingBlack)[half] \
                for half in range(2)]
        else:
            return [0, 0]


    def inCheck(self, piece, playingBlack):
        if not self.check or self.board[piece].upper() == 'K': return [4294967295, 4294967295]
        if self.kAttacker1 > -1 and self.kAttacker2 > -1:
            return [0, 0]
        return self.protectingKing(self.kAttacker1, playingBlack)


    def protectingKing(self, piece, playingBlack):
        if self.board[piece].upper() == 'K': return [4294967295, 4294967295]
        if playingBlack:
            iKing = self.board.find('K')
        else:
            iKing = self.board.find('k')
        dirs = {
            'N': ((iKing - piece) % 8 == 0 and piece < iKing),
            'NW': ((iKing - piece) % 9 == 0 and piece < iKing and piece % 8 < iKing % 8),
            'NE': ((iKing - piece) % 7 == 0 and piece < iKing and piece % 8 > iKing % 8),
            'W': (iKing // 8 == piece // 8 and piece < iKing),
            'E': (iKing // 8 == piece // 8 and piece > iKing),
            'SW': ((iKing - piece) % 7 == 0 and piece > iKing and piece % 8 < iKing % 8),
            'SE': ((iKing - piece) % 9 == 0 and piece > iKing and piece % 8 > iKing % 8),
            'S': ((iKing - piece) % 8 == 0 and piece > iKing)
        }
        
        for direction in dirs:
            if dirs[direction]:
                return self.directions(iKing, playingBlack, direction, checkThreats=True)
        return [4294967295, 4294967295]


    def toBitset(self, square, bitset):
        bitset[square // 32] += 1 << (31 - (square % 32))
        return bitset


    def pawnMoves(self, piece, playingBlack, attacks=False):
        legalMoves = [0, 0]
        if playingBlack:
            forward = 8
            iAttacks = (7, 9)
        else:
            forward = -8
            iAttacks = (-7, -9)
        canCapture = lambda inPath : (playingBlack and inPath == inPath.lower()) or (not playingBlack and inPath == inPath.upper())
        for attack in iAttacks:
            if (piece + attack) // 8 != (piece + forward) // 8 or \
                0 > piece + attack > 63: continue
            if attacks or (
                self.board[piece + attack] != '0' and (
                (self.board[piece + attack] == self.board[piece + attack].upper()) != playingBlack or \
                piece + attack == self.enPassant)):
                legalMoves = self.toBitset(piece + attack, legalMoves)
  
        if not attacks and -1 < piece + forward < 64 and self.board[piece + forward] == '0':
            legalMoves = self.toBitset(piece + forward, legalMoves)
            if playingBlack and 7 < piece < 16 and self.board[piece + forward * 2] == '0':
                legalMoves = self.toBitset(piece + forward * 2, legalMoves)
            elif not playingBlack and 47 < piece < 56 and self.board[piece + forward * 2] == '0':
                legalMoves = self.toBitset(piece + forward * 2, legalMoves)
        return legalMoves


    def kingMoves(self, piece, playingBlack, attacks=False):
        moves = self.directions(piece, playingBlack, 'N', 'NW', 'NE', 'W', 'E', 'SW', 'SE', 'S', rng=2, attacks=attacks)
        if playingBlack:
            eAttacks = [self.wAttacksTop, self.wAttacksBottom]
        else:
            eAttacks = [self.bAttacksTop, self.bAttacksBottom]
        return [moves[half] - (eAttacks[half] & moves[half]) for half in range(2)]


    def queenMoves(self, piece, playingBlack, attacks=False):
        return self.directions(piece, playingBlack, 'N', 'NW', 'NE', 'W', 'E', 'SW', 'SE', 'S', attacks=attacks)

    # def scan(self, square, playingBlack, direction, attacks=False):
    #     bitset = [0, 0]
    #     dirs = {
    #         'N': (-8, lambda sq : sq > -1),
    #         'NW': (-9, lambda sq : sq > -1 and sq % 8 < 7),
    #         'NE': (-7, lambda sq : sq > -1 and sq % 8 > 0),
    #         'W': (-1, lambda sq : sq % 8 < piece % 8),
    #         'E': (1, lambda sq : sq % 8 > piece % 8),
    #         'SW': (7, lambda sq : sq < 64 and sq % 8 < 7),
    #         'SE':(9, lambda sq : sq < 64 and sq % 8 > 0),
    #         'S': (8, lambda sq : sq < 64)
    #     }
    #     for distance in range(1, 8):
    #         current = square + dirs[direction][0] * distance
    #         if dirs[direction][1](current):
    #             if self.board[current] == '0':
    #                 bitset = self.toBitset(current, bitset)
    #                 continue
    #             if (playingBlack and self.board[current] == self.board[current].lower()) \
    #                 or (not playingBlack and self.board[current] == self.board[current].upper()):
    #                 bitset = self.toBitset(current, bitset)
    #             elif attacks:
    #                 bitset = self.toBitset(currnt, bitset)
    #         return bitset


    def directions(self, piece, playingBlack, *args, rng=8, checkThreats=False, attacks=False):
        legalMoves = [0, 0]
        dirs = {
            'N': (-8, lambda sq : sq > -1, ('Q', 'R')),
            'NW': (-9, lambda sq : sq > -1 and sq % 8 < 7, ('Q', 'B')),
            'NE': (-7, lambda sq : sq > -1 and sq % 8 > 0, ('Q', 'B')),
            'W': (-1, lambda sq : sq % 8 < piece % 8, ('Q', 'R')),
            'E': (1, lambda sq : sq % 8 > piece % 8, ('Q', 'R')),
            'SW': (7, lambda sq : sq < 64 and sq % 8 < 7, ('Q', 'B')),
            'SE':(9, lambda sq : sq < 64 and sq % 8 > 0, ('Q', 'B')),
            'S': (8, lambda sq : sq < 64, ('Q', 'R'))
        }
        checkSquare = lambda direc, dist : piece + direc * dist
        canCapture = lambda inPath : (playingBlack and inPath == inPath.lower()) or (not playingBlack and inPath == inPath.upper())
        blockers = 0
        for arg in args:
            for sq in range(1, rng):
                current = checkSquare(dirs[arg][0], sq)
                if dirs[arg][1](current):
                    if self.board[current] == '0':
                        legalMoves = self.toBitset(current, legalMoves)
                        continue
                    elif canCapture(self.board[current]):
                        legalMoves = self.toBitset(current, legalMoves)
                        if checkThreats and self.board[current].upper() in dirs[arg][2]:
                            return legalMoves
                        if attacks and self.board[current].upper() == 'K':
                            if self.kAttacker1 == -1: self.kAttacker1 = piece
                            else: self.kAttacker2 = piece
                            self.check = True
                            continue
                    else:
                        if attacks:
                            legalMoves = self.toBitset(current, legalMoves)
                        elif checkThreats:
                            blockers += 1
                            if blockers < 2: continue
                break
        if checkThreats: return [4294967295, 4294967295]
        return legalMoves


    def rookMoves(self, piece, playingBlack, attacks=False):
        return self.directions(piece, playingBlack, 'N', 'S', 'W', 'E', attacks=attacks)


    def knightMoves(self, piece, playingBlack, attacks=False):
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


    def bishopMoves(self, piece, playingBlack, attacks=False):
        return self.directions(piece, playingBlack, 'NW', 'NE', 'SW', 'SE', attacks=attacks)        


    def alterBoard(self, piece, move):
        segments = []
        value = self.board[piece]
        if self.board[move] != '0':
            self.captured += self.board[move]
        if move > piece:
            segments.append(self.board[:piece] + '0')
            segments.append(self.board[piece + 1:move] + value)
            segments.append(self.board[move + 1:])
        else:
            segments.append(self.board[:move] + value)
            segments.append(self.board[move + 1:piece] + '0')
            segments.append(self.board[piece + 1:])
        self.board = segments[0] + segments[1] + segments[2]


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