from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class GameBoard(models.Model):
    whiteUser = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='whiteUser')
    blackUser = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='blackUser')
    timeStarted = models.DateTimeField(default=timezone.now)
    whitesTurn = models.BooleanField(default=True)
    check = models.BooleanField(default=False)
    winner = models.CharField(max_length=1, default='0')
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
        self.check = False
        for sq in range(64):
            if self.board[sq] == '0': continue
            playingBlack = self.board[sq] == self.board[sq].upper()
            attacks = self.movesByPiece[self.board[sq]](self, sq, playingBlack, attacks=True)
            if not playingBlack:
                for half in range(2):
                    wAttacks[half] |= attacks[half]
            else:
                for half in range(2):
                    bAttacks[half] |= attacks[half]
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
                self.setCastles(move[0])
                if not self.alterBoard(move[0], move[1]):
                    return False
                self.whitesTurn = not self.whitesTurn
                self.setAttacks()
                self.isGameOver(playerId)
                self.save()
                return True
        return False


    def setCastles(self, piece):
        if self.castle == 0: pass
        elif piece == 0 and self.castle & 8:
            self.castle -= 8
        elif piece == 7 and self.castle & 4:
            self.castle -= 4
        elif piece == 56 and self.castle & 2:
            self.castle -= 2
        elif piece == 63 and self.castle & 1:
            self.castle -= 1
        elif piece == 4 and (self.castle & 8 or self.castle & 4):
            self.castle -= (8 & self.castle) + (4 & self.castle)
        elif piece == 60 and (self.castle & 2 or self.castle & 1):
            self.castle -= (2 & self.castle) + (1 & self.castle)


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
        myPiece = playingBlack == (self.board[piece] == self.board[piece].upper())
        myTurn = self.whitesTurn != playingBlack
        if myPiece and myTurn:
            protectingKing = self.protectingKing(piece, playingBlack)
            moves = self.movesByPiece[self.board[piece]](self, piece, playingBlack)
            inCheck = self.inCheck(piece, playingBlack)
            return [protectingKing[half] & moves[half] & inCheck[half] for half in range(2)]
        else:
            return [0, 0]


    def inCheck(self, piece, playingBlack):
        if not self.check or self.board[piece].upper() == 'K': return [4294967295, 4294967295]
        if self.kAttacker1 > -1 and self.kAttacker2 > -1:
            return [0, 0]
        if self.board[self.kAttacker1].upper() == 'N' or self.board[self.kAttacker1].upper() == 'P':
            return self.toBitset(self.kAttacker1, [0, 0])
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


    def promote(self, promotion, playerId):
        if playerId == self.blackUser.id:
            piece = self.board[56:].find('P') + 56
        else:
            piece = self.board[:8].find('p')
            promotion = promotion.lower()
        segments = []
        segments.append(self.board[:piece] + promotion)
        segments.append(self.board[piece + 1:])
        self.board = segments[0] + segments[1]
        self.whitesTurn = not self.whitesTurn
        self.setAttacks()
        self.isGameOver(playerId)
        self.save()


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
                if (not playingBlack and self.board[piece + attack] == 'K') \
                    or (playingBlack and self.board[piece + attack] == 'k'):
                    self.putInCheck(piece)
        if not attacks and -1 < piece + forward < 64 and self.board[piece + forward] == '0':
            legalMoves = self.toBitset(piece + forward, legalMoves)
            if playingBlack and 7 < piece < 16 and self.board[piece + forward * 2] == '0':
                legalMoves = self.toBitset(piece + forward * 2, legalMoves)
            elif not playingBlack and 47 < piece < 56 and self.board[piece + forward * 2] == '0':
                legalMoves = self.toBitset(piece + forward * 2, legalMoves)
        return legalMoves


    def castleMoves(self, playingBlack):
        bitset = [0, 0]
        if self.check: return bitset
        castleRight = True
        castleLeft = True
        if playingBlack:
            if self.castle & 8:
                for sq in [1, 2, 3]:
                    if self.board[sq] != '0':
                        castleRight = False
                        break
                for sq in [0, 1, 2, 3]:
                    if self.toBitset(sq, [0, 0])[0] & self.wAttacksTop:
                        castleRight = False
                        break
            else: castleRight = False        
            if self.castle & 4:
                for sq in [5, 6]:
                    if self.board[sq] != '0':
                        castleLeft = False
                        break
                for sq in [5, 6, 7]:
                    if self.toBitset(sq, [0, 0])[0] & self.wAttacksTop:
                        castleLeft = False
                        break
            else: castleLeft = False
            if castleRight:
                bitset = self.toBitset(2, bitset)
            if castleLeft:
                bitset = self.toBitset(6, bitset)
        else:
            if self.castle & 2:
                for sq in [57, 58, 59]:
                    if self.board[sq] != '0':
                        castleLeft = False
                        break
                for sq in [56, 57, 58, 59]:
                    if self.toBitset(sq, [0, 0])[1] & self.bAttacksBottom:
                        castleLeft = False
                        break
            else: castleLeft = False
            if self.castle & 1:
                for sq in [61, 62]:
                    if self.board[sq] != '0':
                        castleRight = False
                        break
                for sq in [61, 62, 63]:
                    if self.toBitset(sq, [0, 0])[1] & self.bAttacksBottom:
                        castleRight = False
                        break
            else: castleRight = False
            if castleLeft:
                bitset = self.toBitset(58, bitset)
            if castleRight:
                bitset = self.toBitset(62, bitset)
        return bitset


    def kingMoves(self, piece, playingBlack, attacks=False):
        moves = self.directions(piece, playingBlack, 'N', 'NW', 'NE', 'W', 'E', 'SW', 'SE', 'S', rng=2, attacks=attacks)
        if attacks:
            return moves
        castleMoves = self.castleMoves(playingBlack)
        if playingBlack:
            eAttacks = [self.wAttacksTop, self.wAttacksBottom]
        else:
            eAttacks = [self.bAttacksTop, self.bAttacksBottom]
        return [(moves[half] + castleMoves[half]) - (eAttacks[half] & moves[half]) for half in range(2)]


    def queenMoves(self, piece, playingBlack, attacks=False):
        return self.directions(piece, playingBlack, 'N', 'NW', 'NE', 'W', 'E', 'SW', 'SE', 'S', attacks=attacks)


    def putInCheck(self, attacker):
        if self.kAttacker1 == -1: self.kAttacker1 = attacker
        else: self.kAttacker2 = attacker
        self.check = True


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
                            self.putInCheck(piece)
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
            if move[1](current):
                if (self.board[current] == '0' or canCapture(self.board[current])):
                    legalMoves = self.toBitset(current, legalMoves)
                    if self.board[current].upper() == 'K':
                        self.putInCheck(piece)
                elif attacks:
                    legalMoves = self.toBitset(current, legalMoves)
        return legalMoves


    def bishopMoves(self, piece, playingBlack, attacks=False):
        return self.directions(piece, playingBlack, 'NW', 'NE', 'SW', 'SE', attacks=attacks)        


    def makeCastleMove(self, move):
        if move == 2:
            self.alterBoard(0, 3)
        elif move == 6:
            self.alterBoard(7, 5)
        elif move == 58:
            self.alterBoard(56, 59)
        elif move == 62:
            self.alterBoard(63, 61)


    def alterBoard(self, piece, move):
        segments = []
        value = self.board[piece]
        if (piece == 4 and value == 'K') or (piece == 60 and value == 'k'):
            self.makeCastleMove(move)
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
        if self.promotion(value, move):
            self.save()
            return False
        return True


    def promotion(self, value, move):
        if value == 'P' and move > 55:
            self.sendPromotion(self.blackUser.id)
            return True
        if value == 'p' and move < 8:
            self.sendPromotion(self.whiteUser.id)
            return True
        return False


    def sendPromotion(self, playerId):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "user%s" % playerId,
            {"type": "promote"}
        )

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