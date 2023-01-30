import sys
sys.path.append('../CHESS')

import os
import pygame

from gameplay.code_game_transfers import (
    array_coords_to_pygame_coords, 
    all_center_coords, 
    find_closest_center_to_click,
    coord_to_index
)
from game_objects.board import board
from legal_moves.moves1_piece_bounds import moves_piece_bounded1

from game_objects.pieces import (
    wk,
    wq,
    wr,
    wkn,
    wb,
    wp,
    bk,
    bq,
    br,
    bkn,
    bb,
    bp,
    DIR,
    PIECE_HEIGHT,
    PIECE_WIDTH
)

pygame.init()

COORDS = all_center_coords()
WIDTH = 640
HIEGHT = 640
WIN = pygame.display.set_mode((WIDTH, HIEGHT))
pygame.display.set_caption("Chess")
FPS = 60

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('images', 'board.png')), (WIDTH, HIEGHT))


def blit_pieces(board): #this will be in the order as the pieces below
    for i_row in range(7):
        for i_col in range(7):
            if type(board[i_row][i_col]) != str:
                piece = board[i_row][i_col]
                img = piece.image
                scaled_image = pygame.transform.scale(pygame.image.load(os.path.join(DIR, img)), (PIECE_WIDTH, PIECE_HEIGHT))
                WIN.blit(scaled_image, array_coords_to_pygame_coords((i_row, i_col)))

def draw_window():
    WIN.blit(BACKGROUND, (0, 0))
    scaled_image = pygame.transform.scale(pygame.image.load(os.path.join(DIR, wk.image)), (PIECE_WIDTH, PIECE_HEIGHT))
    WIN.blit(scaled_image, array_coords_to_pygame_coords((1, 5)))
    #blit_pieces(location_array)
    
    
    event = pygame.event.wait()
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        #this finds the coordinate of the swquare clicked
        square_center_coords = find_closest_center_to_click(COORDS, mouse_pos)

        #convert back to list index
        index = coord_to_index(square_center_coords)
        moves = moves_piece_bounded1(board, index)
        print(moves)

        
    

    pygame.display.update()

def main():
    #clock = pygame.time.Clock()
    run = True
    while run:
        #clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_window()

    pygame.quit()

if __name__ == "__main__":
    main()