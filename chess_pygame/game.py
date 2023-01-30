import sys
sys.path.append('../CHESS')

import os
import time
import pygame
from gameplay.code_game_transfers import array_coords_to_pygame_coords
from game_objects.pieces import (
    WHITE_KING,
    WHITE_QUEEN,
    WHITE_ROOK,
    WHITE_KNIGHT,
    WHITE_BISHOP,
    WHITE_PAWN,
    BLACK_KING,
    BLACK_QUEEN,
    BLACK_ROOK,
    BLACK_KNIGHT,
    BLACK_BISHOP,
    BLACK_PAWN
)

pygame.init()

WIDTH = 640
HIEGHT = 640
WIN = pygame.display.set_mode((WIDTH, HIEGHT))
pygame.display.set_caption("Chess")
FPS = 60

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('images', 'board.png')), (WIDTH, HIEGHT))

location_array = [(i-i,0) for i in range(12)]
def blit_pieces(location_array): #this will be in the order as the pieces below

    WIN.blit(WHITE_KING, (location_array[0][0], location_array[0][1]))
    WIN.blit(WHITE_QUEEN, (location_array[1][0], location_array[1][1]))
    WIN.blit(WHITE_ROOK, (location_array[2][0], location_array[2][1]))
    WIN.blit(WHITE_KNIGHT, (location_array[3][0], location_array[3][1]))
    WIN.blit(WHITE_BISHOP, (location_array[4][0], location_array[4][1]))
    WIN.blit(WHITE_PAWN, (location_array[5][0], location_array[5][1]))
    WIN.blit(BLACK_KING, (location_array[6][0], location_array[6][1]))
    WIN.blit(BLACK_QUEEN, (location_array[7][0], location_array[7][1]))
    WIN.blit(BLACK_ROOK, (location_array[8][0], location_array[8][1]))
    WIN.blit(BLACK_KNIGHT, (location_array[9][0], location_array[9][1]))
    WIN.blit(BLACK_BISHOP, (location_array[10][0], location_array[10][1]))
    WIN.blit(BLACK_PAWN, (location_array[11][0], location_array[11][1]))


def draw_window():
    WIN.blit(BACKGROUND, (0, 0))
    WIN.blit(WHITE_KING, array_coords_to_pygame_coords((1, 5)))
    #blit_pieces(location_array)
    

    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_window()

    pygame.quit()

if __name__ == "__main__":
    main()