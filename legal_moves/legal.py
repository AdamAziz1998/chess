import sys
sys.path.append('../CHESS')

from legal_moves.sudo_legal import moves_piece_bounded
from legal_moves.move_categories import Move, direction

def pawn_moves_filtered(sudo_moves):
    legal_moves = []
    for sudo_move in sudo_moves:
        if len(sudo_move.direction) == 3 and 'k' in sudo_move.type:
            legal_moves.append(sudo_move)
        elif len(sudo_move.direction) == 1 and sudo_move.type == 'x ':
            legal_moves.append(sudo_move)
    return legal_moves

def double_first_pawn_move(piece, board, location_index):
    if piece.move0:
        #if starting on the upper side of the board
        if location_index == 6:
            square_infront1 = board[location_index[0] - 1][location_index[1]]
            square_infront2 = board[location_index[0] - 2][location_index[1]]
            new_loc = (location_index[0] - 2, location_index[1])
        #if starting on the lower side of hte board
        else:
            square_infront1 = board[location_index[0] + 1][location_index[1]]
            square_infront2 = board[location_index[0] + 2][location_index[1]]
            new_loc = (location_index[0] + 2, location_index[1])
        
        #checking that there are no other pieces in the way of the board
        if type(square_infront1) == str and type(square_infront2) == str:
            move_coord = new_loc
            dir = direction(move_coord, location_index)
            move = Move(location_index, new_loc, 'x ', 2, dir)

        else:
            move =  False
    else: move = False

    return move

def en_passant(board, location_index, piece, current_moves):
    #if in the right location and piece to the left is en-passantable
    if location_index[0] == 3 or location_index[0] == 4:
        if location_index[1] == 7:
            piece_to_right = False
            piece_to_left = board[location_index[0]][location_index[1] - 1]
        elif location_index[1] == 0:
            piece_to_right = board[location_index[0]][location_index[1] + 1]
            piece_to_left = False
        else:
            piece_to_right = board[location_index[0]][location_index[1] + 1]
            piece_to_left = board[location_index[0]][location_index[1] - 1]

        if False:#need to continue here as i was too tired to contiunue
            pass


    #if in the right location and piece to the right is en-passantable
    elif False:
        pass

    else:
        passant_move = False

    return passant_move


def king_side_castling(board, sudo_moves, piece):
    pass

def queen_side_castleing(board, sudo_moves):
    pass

def end_of_file_pawn(board, sudo_moves, new_piece_type):
    pass

def check_checker(board):
    pass

def check_move_filter(board, all_moves):
    pass

def pins(board):
    pass




def legal_moves(board, location_index):
    moves = moves_piece_bounded(board, location_index)

    piece = board[location_index[0]][location_index[1]]
    
    if piece.type == 'p':
        moves = pawn_moves_filtered(moves)
        
        doubled_move = double_first_pawn_move(piece, board, location_index)
        if doubled_move:
            moves.append(doubled_move)

        #passant_move = en_passant()
        #if passant_move:
        #    moves.append(passant_move)

    return moves




def display_moves(board, location_index):
    i, j = location_index
    if type(board[i][j]) != str:
        return legal_moves(board, location_index)
    else:
        return []

def display_legal_moves(board, location_index):
    moves = display_moves(board, location_index)

    for move in moves:
        i, j = move.location_index
        board[i][j] = move.type

    return board