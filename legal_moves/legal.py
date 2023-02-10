import sys
sys.path.append('../CHESS')

from legal_moves.sudo_legal import moves_piece_bounded
from legal_moves.move_categories import Move, direction
from gameplay.turn import make_move
from game_objects.pieces import br, wr
import copy

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
        if location_index[0] == 6:
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

def check_en_passant_available(board, dir, location_index):
    my_pawn = board[location_index[0]][location_index[1]]
    if dir == 'l':
        square = board[location_index[0]][location_index[1] - 1]
        if type(square) != str and square.type == 'p' and square.move1 and square.team != my_pawn.team:
            return True
        else:
            return False
    else:
        square = board[location_index[0]][location_index[1] + 1]
        if type(square) != str and square.type == 'p' and square.move1 and square.team != my_pawn.team:
            return True
        else:
            return False

def en_passant(board, location_index, piece):
    #if in the right location and piece to the left is en-passantable
    move = False

    if piece.team == 'b':
        dir = -1
    else:
        dir = 1

    if location_index[0] == 3 or location_index[0] == 4:
        if location_index[1] == 7:
            passant_to_left = check_en_passant_available(board, 'l', location_index)
            if passant_to_left:
                move = Move(location_index, (location_index[0] + dir, location_index[1] - 1), 'p', 1, 'l')
        elif location_index[1] == 0:
            passant_to_right = check_en_passant_available(board, 'r', location_index)
            if passant_to_right:
                move = Move(location_index, (location_index[0] + dir, location_index[1] + 1), 'p', 1, 'r')
        else:
            passant_to_right = check_en_passant_available(board, 'r', location_index)
            passant_to_left = check_en_passant_available(board, 'l', location_index)
            if passant_to_right:
                move = Move(location_index, (location_index[0] + dir, location_index[1] + 1), 'p', 1, 'r')

            if passant_to_left:
                move = Move(location_index, (location_index[0] + dir, location_index[1] - 1), 'p', 1, 'l')

    return move

def end_of_file_pawn(location_index, piece, moves):
    if (location_index[0] == 1 or location_index[0] == 6) and not piece.move0:
        for end_move in moves:
            end_move.type = 't'
    return moves

#the view of the pieces will not have the be in the input "team"
def attack_view(board, team):
    view = []
    for row in range(len(board)):
        for el in range(len(board)):
            if board[row][el] != '  ' and board[row][el].type != 'p' and board[row][el].team != team:
                location_index = (row, el)
                moves = moves_piece_bounded(board, location_index)
                new_views = [move.location_index for move in moves if move.location_index not in view]
                view += new_views
            elif board[row][el] != '  ' and board[row][el].type == 'p' and board[row][el].team != team:
                location_index = (row, el)
                moves = moves_piece_bounded(board, location_index)
                new_views = [move.location_index for move in moves if move.location_index not in view and len(move.direction) == 3]
                view += new_views
    return view

def check_checker(board, king_location_index):
    ki, kj = king_location_index
    view = attack_view(board, board[ki][kj].team)
    return True if (ki, kj) in view else False

def king_side_castling(board, piece):
    if piece.team == 'w':
        i_loc = 0
    else:
        i_loc = 7
    #assuming no checks
    move = False
    if  board[i_loc][6] == '  ' and board[i_loc][5] == '  ' and piece.move0:
        potential_rook = board[i_loc][7]
        if type(potential_rook) != str and potential_rook.move0:
            move =  Move((i_loc, 4), (i_loc, 6), 'kc', 2, 'r')

    #checking if move is legal
    check = check_checker(board, (i_loc, 4))
    view = attack_view(board, board[i_loc][4].team)
    if check or (i_loc, 6) in view or (i_loc, 5) in view:
        return False
    else:
        return move

def queen_side_castling(board, piece):
    if piece.team == 'w':
        i_loc = 0
    else:
        i_loc = 7

    move = False
    if board[i_loc][3] ==  board[i_loc][2] == board[i_loc][1] == '  ' and piece.move0:
        potential_white_rook = board[i_loc][0]
        if type(potential_white_rook) != str and potential_white_rook.move0:
            move =  Move((i_loc, 4), (i_loc, 2), 'qc', 2, 'l')
    
    #checking if move is legal
    check = check_checker(board, (i_loc, 4))
    view = attack_view(board, board[i_loc][4].team)
    if check or (i_loc, 2) in view or (i_loc, 3) in view:
        return False
    else:
        return move


def check_filter(board, moves, king_location_index, location_index, team):
    checked_moves = []
    for move in moves:
        #pretend move taken and check for a check
        board_copy = copy.deepcopy(board)
        if move.type == 't':
            pawn_transform_piece = br if team == 'b' else wr
        else:
            pawn_transform_piece = False

        sudo_move = make_move(board_copy, location_index, move.location_index, move, pawn_transform_piece)
        
        if king_location_index == location_index:
            post_move_checker = check_checker(sudo_move, move.location_index)
        else:
            post_move_checker = check_checker(sudo_move, king_location_index)

        if not post_move_checker:
            checked_moves.append(move)
    return checked_moves

def king_find(board, team):
    found = False
    king_coords = (0,0)
    for i in range(len(board)):
        for j in range(len(board)):
            if type(board[i][j]) != str and board[i][j].type == 'k' and board[i][j].team == team:
                found = True
                king_coords = (i, j)
                break
        
        if found:
            break
    return king_coords
                

def legal_moves(board, location_index):
    moves = moves_piece_bounded(board, location_index)
    piece = board[location_index[0]][location_index[1]]
    team = piece.team
    
    if piece.type == 'p':
        moves = pawn_moves_filtered(moves)
        
        doubled_move = double_first_pawn_move(piece, board, location_index)
        if doubled_move:
            moves.append(doubled_move)

        passant_move = en_passant(board, location_index, piece)
        if passant_move:
            moves.append(passant_move)

        moves = end_of_file_pawn(location_index, piece, moves)

    elif piece.type == 'k' and piece.move0 == True:
        king_side_castle = king_side_castling(board, piece)
        if king_side_castle:
            moves.append(king_side_castle)
        queen_side_castle = queen_side_castling(board, piece)
        if queen_side_castle:
            moves.append(queen_side_castle)

    king_location_index = king_find(board, team)
    ki, kj = king_location_index
    king = board[ki][kj]
    team = king.team
    moves = check_filter(board, moves, king_location_index, location_index, team)

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