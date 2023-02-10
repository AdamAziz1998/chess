import sys
sys.path.append('../CHESS')

from legal_moves.legal import legal_moves
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

            ai_moves += [move1, move2, move3, move4]
    return ai_moves

def random_moving_bot(board, ai_team):
    ai_moves = all_potential_moves(board, ai_team)
    
    return random.choice(ai_moves)



