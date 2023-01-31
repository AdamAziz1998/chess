import sys
sys.path.append('../CHESS')

import os
import pygame

from gameplay.code_game_transfers import (
    array_coords_to_pygame_coords, 
    array_coords_to_pygame_coords_circle, 
    array_coords_to_pygame_coords_kill_circle,
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

CENTER_COORDS = all_center_coords()
WIDTH = 640
HIEGHT = 640
WIN = pygame.display.set_mode((WIDTH, HIEGHT))
pygame.display.set_caption("Chess")
FPS = 60

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('images', 'board.png')), (WIDTH, HIEGHT))
PIECE_SELECTED = False
MY_TEAM = 'w'
PREVIOUS_SELECTED_COORDS = (-10, -10)

def blit_pieces(board): #this will be in the order as the pieces below
    for i_row in range(7):
        for i_col in range(7):
            if type(board[i_row][i_col]) != str:
                piece = board[i_row][i_col]
                img = piece.image
                scaled_image = pygame.transform.scale(pygame.image.load(os.path.join(DIR, img)), (PIECE_WIDTH, PIECE_HEIGHT))
                WIN.blit(scaled_image, array_coords_to_pygame_coords((i_row, i_col)))

def blit_moves(moves):
    move_coords = [move.location_index for move in moves]
    move_types = [move.type for move in moves]

    radius = 12
    circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    circle1 = pygame.Surface(((radius + 8) * 2, (radius + 8) * 2), pygame.SRCALPHA)
    
    for move_coord, move_type in zip(move_coords, move_types):
        pygame_move_coord = array_coords_to_pygame_coords_circle(move_coord)

        if move_type == 'x ':
            #this is a normal move
            pygame_move_coord = array_coords_to_pygame_coords_circle(move_coord)
            pygame.draw.circle(circle, (0, 0, 0, 128), (radius, radius), radius)
            WIN.blit(circle, pygame_move_coord)
            
        else:
            #this is a kill move
            pygame_move_coord = array_coords_to_pygame_coords_kill_circle(move_coord)
            pygame.draw.circle(circle1, (0, 0, 0, 128), (radius + 8, radius + 8), radius + 8, width=4)
            WIN.blit(circle1, pygame_move_coord)

def draw_window():
    global PIECE_SELECTED, PREVIOUS_SELECTED_COORDS

    WIN.blit(BACKGROUND, (0, 0))
    
    event = pygame.event.wait()
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        #this finds the coordinate of the swquare clicked
        square_center_coords = find_closest_center_to_click(CENTER_COORDS, mouse_pos)

        #convert back to list index
        index = coord_to_index(square_center_coords)
        

        #here we need to check if the moves are from this team or a different team
        #if its from this team then show the potential moves for this piece 
        #if its not from my team then new nested if condition below
        #if i have a kill circle on this then kill function will go there
            
        moves = moves_piece_bounded1(board, index)
        if len(moves) != 0:
            PIECE_SELECTED = True
            PREVIOUS_SELECTED_COORDS = index
        else:
            PIECE_SELECTED = False
    
    if PIECE_SELECTED == True:
        moves = moves_piece_bounded1(board, PREVIOUS_SELECTED_COORDS)
        blit_moves(moves)

    blit_pieces(board)

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