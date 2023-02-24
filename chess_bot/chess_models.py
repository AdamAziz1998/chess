import sys
sys.path.append('../CHESS')

from legal_moves.legal import legal_moves, check_checker, king_find
from legal_moves.move_categories import Move
from gameplay.turn import turn
from game_objects.board import starting_board
from game_objects.pieces import Piece, wb, bb, wq, bq, wr, br, wkn, bkn 
import random

#firstly I need to make the ability for the bot to mkae a move possible
def all_potential_moves(board, team):
    coords = []
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != '  ' and board[i][j].team == team:
                coords.append((i, j))

    ai_moves = []
    
    for coord in coords:
        piece_moves = legal_moves(board, coord)
        ai_moves += piece_moves

    ai_moves1 = []

    for move in ai_moves: 
        if move.type == 't':
            ai_moves.pop(ai_moves.index(move))
            img1 = wq.image if team == 'w' else bq.image
            move1 = Move(
                move.org_location, 
                move.location_index, 
                move.type, 
                move.distance, 
                move.direction, 
                Piece(team, 'q', img1, False, False)
            )
            img2 = wb.image if team == 'w' else bb.image
            move2 = Move(
                move.org_location, 
                move.location_index, 
                move.type, 
                move.distance, 
                move.direction, 
                Piece(team, 'b', img2, False, False)
            )
            img3 = wkn.image if team == 'w' else bkn.image
            move3 = Move(
                move.org_location, 
                move.location_index, 
                move.type, 
                move.distance, 
                move.direction, 
                Piece(team, 'n', img3, False, False)
            )
            img4 = wr.image if team == 'w' else br.image
            move4 = Move(
                move.org_location, 
                move.location_index, 
                move.type, 
                move.distance, 
                move.direction, 
                Piece(team, 'r', img4, False, False)
            )

            ai_moves1 += [move1, move2, move3, move4]
        else:
            ai_moves1.append(move)
    return ai_moves1

def random_moving_bot(board, ai_team):
    ai_moves = all_potential_moves(board, ai_team)
    return random.choice(ai_moves)


def point_type(piece_type):
    if piece_type == 'q':
        return 9
    elif piece_type == 'r':
        return 5
    elif piece_type == 'n' or piece_type == 'b':
        return 3
    elif piece_type == 'p':
        return 1
    else:
        return None

def checkmate_checker(all_moves, check):
    if check and all_moves == []:
        return True
    else:
        return False

def stale_mate_checker(all_moves, check):
    if all_moves == [] and not check:
        return True
    else:
        return False

def endgame_checkers(board, kill, team):
    king_coords = king_find(board, team)
    all_moves = all_potential_moves(board, team)
    check = check_checker(board, king_coords)

    if checkmate_checker(all_moves, check):
        return 'checkmate'

    elif stale_mate_checker(all_moves, check):
        return 'stalemate'
    #draw condition
    elif kill == 100:
        return 'draw'

    #draw by repitition can be added later

    else:
        return 'continue'

    # if there is less than 5 pieces on the board and is losing then assume a stalemate to be equivalent to a win

#if team == 'w' this will return the score of whites pieces compared to blacks pieces and vice versa
def game_scoring(board, team):
    all_moves = all_potential_moves(board, team)
    king_coords = king_find(board, team)
    check = check_checker(board, king_coords)

    if checkmate_checker(all_moves, check):
        return -1000

    white_pieces = []
    black_pieces = []
    for i1 in range(len(board)):
        for j1 in range(len(board)):
            if type(board[i1][j1]) != str:
                if board[i1][j1].team == 'w':
                    white_pieces.append(board[i1][j1])
                else:
                    black_pieces.append(board[i1][j1])
    
    w_points = [point_type(w_piece.type) for w_piece in white_pieces if point_type(w_piece.type) != None]
    b_points = [point_type(b_piece.type) for b_piece in black_pieces if point_type(b_piece.type) != None]
    total_points = sum(w_points) - sum(b_points)
    if team == 'b':
        total_points = - total_points
    
    #stalemate = stale_mate_checker(all_moves, check)

    #if total_points > 0 and stalemate:
    #    return -500
    return total_points
