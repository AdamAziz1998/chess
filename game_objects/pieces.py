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
WHITE_KING_IMAGE = pygame.image.load(os.path.join(DIR, wk.image))
WHITE_QUEEN_IMAGE = pygame.image.load(os.path.join(DIR, wq.image))
WHITE_ROOK_IMAGE = pygame.image.load(os.path.join(DIR, wr.image))
WHITE_KNIGHT_IMAGE = pygame.image.load(os.path.join(DIR, wkn.image))
WHITE_BISHOP_IMAGE = pygame.image.load(os.path.join(DIR, wb.image))
WHITE_PAWN_IMAGE = pygame.image.load(os.path.join(DIR, wp.image))
BLACK_KING_IMAGE = pygame.image.load(os.path.join(DIR, bk.image))
BLACK_QUEEN_IMAGE = pygame.image.load(os.path.join(DIR, bq.image))
BLACK_ROOK_IMAGE = pygame.image.load(os.path.join(DIR, br.image))
BLACK_KNIGHT_IMAGE = pygame.image.load(os.path.join(DIR, bkn.image))
BLACK_BISHOP_IMAGE = pygame.image.load(os.path.join(DIR, bb.image))
BLACK_PAWN_IMAGE = pygame.image.load(os.path.join(DIR, bp.image))

PIECE_WIDTH, PIECE_HEIGHT = 50, 50

WHITE_KING = pygame.transform.scale(WHITE_KING_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
WHITE_QUEEN = pygame.transform.scale(WHITE_QUEEN_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
WHITE_ROOK = pygame.transform.scale(WHITE_ROOK_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
WHITE_KNIGHT = pygame.transform.scale(WHITE_KNIGHT_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
WHITE_BISHOP = pygame.transform.scale(WHITE_BISHOP_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
WHITE_PAWN = pygame.transform.scale(WHITE_PAWN_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
BLACK_KING = pygame.transform.scale(BLACK_KING_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
BLACK_QUEEN = pygame.transform.scale(BLACK_QUEEN_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
BLACK_ROOK = pygame.transform.scale(BLACK_ROOK_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
BLACK_KNIGHT = pygame.transform.scale(BLACK_KNIGHT_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
BLACK_BISHOP = pygame.transform.scale(BLACK_BISHOP_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))
BLACK_PAWN = pygame.transform.scale(BLACK_PAWN_IMAGE, (PIECE_WIDTH, PIECE_HEIGHT))


PIECE = pygame.transform.scale(pygame.image.load(os.path.join(DIR, bp.image)), (PIECE_WIDTH, PIECE_HEIGHT))