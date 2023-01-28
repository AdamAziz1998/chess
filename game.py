import os
import time
import pygame

from pieces import (
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

WIN = pygame.display.set_mode((640, 640))
pygame.display.set_caption("Chess")
FPS = 60

def draw_window():
    WIN.fill((0,100,100))
    WIN.blit(WHITE_KING, (0, 0))
    WIN.blit(WHITE_QUEEN, (0, 0))
    WIN.blit(WHITE_ROOK, (0, 0))
    WIN.blit(WHITE_KNIGHT, (0, 0))
    WIN.blit(WHITE_BISHOP, (0, 0))
    WIN.blit(WHITE_PAWN, (0, 0))
    WIN.blit(BLACK_KING, (0, 0))
    WIN.blit(BLACK_QUEEN, (0, 0))
    WIN.blit(BLACK_ROOK, (0, 0))
    WIN.blit(BLACK_KNIGHT, (0, 0))
    WIN.blit(BLACK_BISHOP, (0, 0))
    WIN.blit(BLACK_PAWN, (0, 0))
    

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