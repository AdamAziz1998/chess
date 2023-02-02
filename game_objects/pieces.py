import pygame
import os

class Piece:
    def __init__(self, team, type, image, move0, move1):
        self.team = team
        self.type = type
        self.image = image
        self.move0 = move0
        self.move1 = move1
   

wk = Piece('w', 'k', 'white_king.png', True, False)
wq = Piece('w', 'q', 'white_queen.png', True, False)
wr = Piece('w', 'r', 'white_rook.png', True, False)
wkn = Piece('w', 'n', 'white_knight.png', True, False)
wb = Piece('w', 'b', 'white_bishop.png', True, False)
wp = Piece('w', 'p', 'white_pawn.png', True, False)
bk = Piece('b', 'k', 'black_king.png', True, False)
bq = Piece('b', 'q', 'black_queen.png', True, False)
br = Piece('b', 'r', 'black_rook.png', True, False)
bkn = Piece('b', 'n', 'black_knight.png', True, False)
bb = Piece('b', 'b', 'black_bishop.png', True, False)
bp = Piece('b', 'p', 'black_pawn.png', True, False)

DIR = 'images'

PIECE_WIDTH, PIECE_HEIGHT = 50, 50