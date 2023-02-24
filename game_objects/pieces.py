import pygame
import os

class Piece:
    def __init__(self, team, type, image, move0, move1):
        self.team = team
        self.type = type
        self.image = image
        self.move0 = move0
        self.move1 = move1
        

# using for the images
wk = Piece('w', 'k', 'white_king.png', True, False)
wq = Piece('w', 'q', 'white_queen.png', True, False)
bk = Piece('b', 'k', 'black_king.png', True, False)
bq = Piece('b', 'q', 'black_queen.png', True, False)
wr = Piece('w', 'r', 'white_rook.png', True, False)
wkn = Piece('w', 'n', 'white_knight.png', True, False)
wb = Piece('w', 'b', 'white_bishop.png', True, False)
br = Piece('b', 'r', 'black_rook.png', True, False)
bkn = Piece('b', 'n', 'black_knight.png', True, False)
bb = Piece('b', 'b', 'black_bishop.png', True, False)
wp = Piece('w', 'p', 'white_pawn.png', True, False)
bp = Piece('b', 'p', 'black_pawn.png', True, False)


   
#singular pieces
wk1 = Piece('w', 'k', 'white_king.png', True, False)
wq1 = Piece('w', 'q', 'white_queen.png', True, False)

bk1 = Piece('b', 'k', 'black_king.png', True, False)
bq1 = Piece('b', 'q', 'black_queen.png', True, False)

#binary pieces
wr1 = Piece('w', 'r', 'white_rook.png', True, False)
wr2 = Piece('w', 'r', 'white_rook.png', True, False)
wkn1 = Piece('w', 'n', 'white_knight.png', True, False)
wkn2 = Piece('w', 'n', 'white_knight.png', True, False)
wb1 = Piece('w', 'b', 'white_bishop.png', True, False)
wb2 = Piece('w', 'b', 'white_bishop.png', True, False)

br1 = Piece('b', 'r', 'black_rook.png', True, False)
br2 = Piece('b', 'r', 'black_rook.png', True, False)
bkn1 = Piece('b', 'n', 'black_knight.png', True, False)
bkn2 = Piece('b', 'n', 'black_knight.png', True, False)
bb1 = Piece('b', 'b', 'black_bishop.png', True, False)
bb2 = Piece('b', 'b', 'black_bishop.png', True, False)

#pawns
wp1 = Piece('w', 'p', 'white_pawn.png', True, False)
wp2 = Piece('w', 'p', 'white_pawn.png', True, False)
wp3 = Piece('w', 'p', 'white_pawn.png', True, False)
wp4 = Piece('w', 'p', 'white_pawn.png', True, False)
wp5 = Piece('w', 'p', 'white_pawn.png', True, False)
wp6 = Piece('w', 'p', 'white_pawn.png', True, False)
wp7 = Piece('w', 'p', 'white_pawn.png', True, False)
wp8 = Piece('w', 'p', 'white_pawn.png', True, False)

bp1 = Piece('b', 'p', 'black_pawn.png', True, False)
bp2 = Piece('b', 'p', 'black_pawn.png', True, False)
bp3 = Piece('b', 'p', 'black_pawn.png', True, False)
bp4 = Piece('b', 'p', 'black_pawn.png', True, False)
bp5 = Piece('b', 'p', 'black_pawn.png', True, False)
bp6 = Piece('b', 'p', 'black_pawn.png', True, False)
bp7 = Piece('b', 'p', 'black_pawn.png', True, False)
bp8 = Piece('b', 'p', 'black_pawn.png', True, False)


DIR = 'images'

PIECE_WIDTH, PIECE_HEIGHT = 50, 50


#non first move pieces
#singular pieces
wk2 = Piece('w', 'k', 'white_king.png', True, False)
wq2 = Piece('w', 'q', 'white_queen.png', True, False)

bk2 = Piece('b', 'k', 'black_king.png', True, False)
bq2 = Piece('b', 'q', 'black_queen.png', True, False)

#binary pieces
wr3 = Piece('w', 'r', 'white_rook.png', True, False)
wr4 = Piece('w', 'r', 'white_rook.png', True, False)
wkn3 = Piece('w', 'n', 'white_knight.png', True, False)
wkn4 = Piece('w', 'n', 'white_knight.png', True, False)
wb3 = Piece('w', 'b', 'white_bishop.png', True, False)
wb4 = Piece('w', 'b', 'white_bishop.png', True, False)

br3 = Piece('b', 'r', 'black_rook.png', True, False)
br4 = Piece('b', 'r', 'black_rook.png', True, False)
bkn3 = Piece('b', 'n', 'black_knight.png', True, False)
bkn4 = Piece('b', 'n', 'black_knight.png', True, False)
bb3 = Piece('b', 'b', 'black_bishop.png', True, False)
bb4 = Piece('b', 'b', 'black_bishop.png', True, False)

#pawns
wp9 = Piece('w', 'p', 'white_pawn.png', False, False)
wp10 = Piece('w', 'p', 'white_pawn.png', False, False)
wp11 = Piece('w', 'p', 'white_pawn.png', False, False)
wp12 = Piece('w', 'p', 'white_pawn.png', False, False)
wp13 = Piece('w', 'p', 'white_pawn.png', False, False)
wp14 = Piece('w', 'p', 'white_pawn.png', False, False)
wp15 = Piece('w', 'p', 'white_pawn.png', False, False)
wp16 = Piece('w', 'p', 'white_pawn.png', False, False)

bp9 = Piece('b', 'p', 'black_pawn.png', False, False)
bp10 = Piece('b', 'p', 'black_pawn.png', False, False)
bp11 = Piece('b', 'p', 'black_pawn.png', False, False)
bp12 = Piece('b', 'p', 'black_pawn.png', False, False)
bp13 = Piece('b', 'p', 'black_pawn.png', False, False)
bp14 = Piece('b', 'p', 'black_pawn.png', False, False)
bp15 = Piece('b', 'p', 'black_pawn.png', False, False)
bp16 = Piece('b', 'p', 'black_pawn.png', False, False)
