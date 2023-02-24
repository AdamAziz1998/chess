import sys
sys.path.append('../CHESS')

import os
import pygame
from chess_bot.chess_models import random_moving_bot, endgame_checkers
from chess_bot.stockfish_bot import engine_move1

from gameplay.code_game_transfers import (
    array_coords_to_pygame_coords, 
    array_coords_to_pygame_coords_circle, 
    array_coords_to_pygame_coords_kill_circle,
    all_center_coords, 
    find_closest_center_to_click,
    coord_to_index
)
from gameplay.turn import turn
from game_objects.board import starting_board, sample_board, donny_board
from legal_moves.legal import display_moves

from game_objects.pieces import (
    Piece,
    wq,
    wr,
    wkn,
    wb,
    bq,
    br,
    bkn,
    bb,
    DIR,
    PIECE_HEIGHT,
    PIECE_WIDTH
)

board = donny_board

pygame.init()

CENTER_COORDS = all_center_coords()
UI_SPACE = 80
WIDTH = 640
HIEGHT = 640 + UI_SPACE
WIN = pygame.display.set_mode((WIDTH, HIEGHT))
pygame.display.set_caption("Chess")
FPS = 60

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('images', 'board.png')), (WIDTH, HIEGHT - UI_SPACE))
PIECE_SELECTED = False
TEAM = 'w'
PREVIOUS_SELECTED_COORDS = (-10, -10)
SELECTED_MOVES_INDEX = []
moves = []
dead_whites = []
dead_blacks = []
pawn_transform = False
pawn_transform_piece = False
kill = 0
mouse_off = False

def blit_pieces(board): #this will be in the order as the pieces below
    for i_row in range(8):
        for i_col in range(8):
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

#pawn_transform will be false if no transformations are happening, otherwise it will be 'w' or 'b' to show what piece to
#  choose to transform the pawn into
def blit_UI(pawn_transform, dead_whites, dead_blacks, TEAM):
    #creating the UI background
    color = (50, 50, 50)
    pygame.draw.rect(WIN, color, pygame.Rect(0, HIEGHT - UI_SPACE, HIEGHT, WIDTH))
    UI_imgs = []

    if TEAM == 'w':
        UI_imgs = [wr.image, wkn.image, wb.image, wq.image]
    elif TEAM == 'b':
        UI_imgs = [br.image, bkn.image, bb.image, bq.image]
    
    if pawn_transform:
        for UI_img in UI_imgs:
            scaled_UI_img = pygame.transform.scale(pygame.image.load(os.path.join(DIR, UI_img)), (PIECE_WIDTH, PIECE_HEIGHT))
            coord_unadj = array_coords_to_pygame_coords((0, UI_imgs.index(UI_img)))
            coord_adj = (coord_unadj[0] + 320, coord_unadj[1] + 80)
            WIN.blit(scaled_UI_img, coord_adj)

def draw_window(single_player: bool, my_team: str, game_status: str):
    global PIECE_SELECTED, PREVIOUS_SELECTED_COORDS, SELECTED_MOVES_INDEX, TEAM
    global board, moves, dead_whites, dead_blacks, pawn_transform, pawn_transform_piece
    global index, move, kill, mouse_off

    WIN.blit(BACKGROUND, (0, 0))
    if not pawn_transform:
        blit_UI(False, False, False, TEAM)
    else:
        blit_UI(TEAM, False, False, TEAM)
    
    if single_player and TEAM != my_team and game_status == 'continue':
        #the bot would go on the line below
        ai_move = engine_move1(board, TEAM, 0, kill)
        print(ai_move.location_index, ai_move.type)
        board, TEAM, kill = turn(board, ai_move.org_location, ai_move.location_index, TEAM, ai_move, ai_move.pawn_transform, kill)

    
    event = pygame.event.wait()
    if event.type == pygame.MOUSEBUTTONDOWN and (TEAM == my_team or not single_player) and game_status == 'continue' and not mouse_off:
        mouse_pos = pygame.mouse.get_pos()

        #if board is clicked
        if mouse_pos[1] < HIEGHT - UI_SPACE and not pawn_transform:

            #this finds the coordinate of the swquare clicked
            square_center_coords = find_closest_center_to_click(CENTER_COORDS, mouse_pos)

            #convert back to list index
            index = coord_to_index(square_center_coords)
            

            #if there is a piece in my team
            if type(board[index[0]][index[1]]) != str and board[index[0]][index[1]].team == TEAM:
                moves = display_moves(board, index)
                PIECE_SELECTED = True
                PREVIOUS_SELECTED_COORDS = index
                SELECTED_MOVES_INDEX = [i.location_index for i in moves]

            #also if this is a move square
            elif index in SELECTED_MOVES_INDEX:
                move = moves[SELECTED_MOVES_INDEX.index(index)]
                if move.type != 't':
                    board, TEAM, kill = turn(board, PREVIOUS_SELECTED_COORDS, index, TEAM, move, False, kill)
                    SELECTED_MOVES_INDEX = []
                    PIECE_SELECTED = False
                    
                else:
                    pawn_transform = True

            else:
                PIECE_SELECTED = False
                SELECTED_MOVES_INDEX = []
        #if the UI is clicked and in pawn_tranform mode
        elif mouse_pos[1] > HIEGHT - UI_SPACE and pawn_transform:
            #part of the UI selected 
            x_mouse_pos = mouse_pos[0]

            #trnasform to queen
            if 640 - 80 < x_mouse_pos < 640:
                img = wq.image if TEAM == 'w' else bq.image
                pawn_transform_piece = Piece(TEAM, 'q', img, False, False)

            #transform to bishop
            elif 640 - 160 < x_mouse_pos < 640 - 80:
                img = wb.image if TEAM == 'w' else bb.image
                pawn_transform_piece = Piece(TEAM, 'b', img, False, False)

            #transform to knight
            elif 640 - 240 < x_mouse_pos < 640 - 160:
                img = wkn.image if TEAM == 'w' else bkn.image
                pawn_transform_piece = Piece(TEAM, 'n', img, False, False)

            #transform to rook
            elif 640 - 320 < x_mouse_pos < 640 - 240:
                img = wr.image if TEAM == 'w' else br.image
                pawn_transform_piece = Piece(TEAM, 'r', img, False, False)
            
            if pawn_transform_piece:
                board, TEAM, kill = turn(board, PREVIOUS_SELECTED_COORDS, index, TEAM, move, pawn_transform_piece, kill)
                SELECTED_MOVES_INDEX = []
                PIECE_SELECTED = False
                pawn_transform = False
                pawn_transform_piece = False
    
    if PIECE_SELECTED:
        moves = display_moves(board, PREVIOUS_SELECTED_COORDS)
        blit_moves(moves)

    if game_status != 'continue':
        mouse_off = True

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

        single_player = True
        my_team = 'b'
        
        game_status = endgame_checkers(board, kill, TEAM)
        
        draw_window(single_player, my_team, game_status)

    pygame.quit()

if __name__ == "__main__":
    main()


#what do i want:
# - create a screenflip for white and black
# - create an annimation for the piece moving from one square to another
# - blit dead pieces on UI