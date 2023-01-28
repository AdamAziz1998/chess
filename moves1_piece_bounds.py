from moves_edge_bounds import (
    rook_moves_unbounded,
    knight_moves_unbounded,
    bishop_moves_unbounded,
    queen_moves_unbounded,
    king_moves_unbounded,
    white_pawn_moves_unbounded,
    black_pawn_moves_unbounded
)
from board import board, starting_board, make_readable

from pieces import (

    wb,
    wp,
    bq

)
from move_categories import Move, distance, direction

def detect_piece_in_path(board, moves, piece, location_index):
    new_moves = []
    for move in moves:
            i1, j1 = move
            piece2 = board[i1][j1]

            dist = distance(move, location_index)
            dir = direction(move, location_index)

            if type(piece2) != str:
                if piece.team != piece2.team:
                    new_moves.append(Move(location_index, (move), 'k' + piece2.type, dist, dir))
            else:
                new_moves.append(Move(location_index, (move), 'x ', dist, dir))

    return new_moves

def bounded_moves(board, location_index):
    i, j = location_index
    piece = board[i][j]

    if type(piece) == str:
        return board

    piece_type = piece.type
    piece_team = piece.team

    if piece_type == 'r':
        moves = rook_moves_unbounded(location_index)
        

    if piece_type == 'n':
        moves = knight_moves_unbounded(location_index)

    if piece_type == 'b':
        moves = bishop_moves_unbounded(location_index)

    if piece_type == 'q':
        moves = queen_moves_unbounded(location_index)

    if piece_type == 'k':
        moves = king_moves_unbounded(location_index)

    if piece_type == 'p' and piece_team == 'w':
        moves = white_pawn_moves_unbounded(location_index)

    if piece_type == 'p' and piece_team == 'b':
        moves = black_pawn_moves_unbounded(location_index)
    

    return moves

def bounded_moves1(board, location_index):
    moves = bounded_moves(board, location_index)

    i, j = location_index
    piece = board[i][j]

    moves1 = detect_piece_in_path(board, moves, piece, location_index)
    return moves1

def bounded_moves_pathed(board, location_index):
    moves = bounded_moves1(board, location_index)

    #get all moves that involve a kill
    kill_moves = [move for move in moves if 'k' in move.type]
    kill_distance_direction = [(move.distance, move.direction) for move in kill_moves]

    valid_moves = []

    for kill_move in kill_moves:
        counter = 0
        for dd in kill_distance_direction:
            if dd[0] < kill_move.distance and dd[1] == kill_move.direction:
                counter += 1
                break
        if counter == 0:
            valid_moves.append(kill_move)

    #get all non killing moves
    x_moves = [move for move in moves if move.type == 'x ']
    x_distance_direction = [(move.distance, move.direction) for move in x_moves]

    #if path is not blocked then the number of moves in same diection with less distance should be distance - 1
    for x_move in x_moves:
        counter = 0

        x_distance = x_move.distance
        x_direction = x_move.direction
        for dd in x_distance_direction:
            if dd[0] < x_distance and x_direction == dd[1]:
                counter += 1
            
        if (x_distance - 1 == counter):
            valid_moves.append(x_move)

    #doing this to all remaining moves to make sure an enemy piece cant be killed if already blocked by a friendly piece
    valid_moves1 = []
    r_distance_direction = [(move.distance, move.direction) for move in valid_moves]

    for v_move in valid_moves:
        counter = 0

        v_distance = v_move.distance
        v_direction = v_move.direction
        for dd in r_distance_direction:
            if dd[0] < v_distance and v_direction == dd[1]:
                counter += 1
            
        if (v_distance - 1 == counter):
            valid_moves1.append(v_move)

    return valid_moves1

def moves_piece_bounded(board, location_index):
    i, j = location_index
    piece_type = board[i][j].type

    if piece_type == 'p' or piece_type == 'n' or piece_type == 'k':
        return bounded_moves1(board, location_index)
    
    else:
        return bounded_moves_pathed(board, location_index)



def display_bounded_moves1(board, location_index):
    moves = moves_piece_bounded(board, location_index)

    for move in moves:
        i, j = move.location_index
        board[i][j] = move.type

    return board

board[5][4] = bq
board[5][3] = wb
board[5][2] = wp
board[5][6] = wp

moves = bounded_moves1(board, (5, 4))

board1 = display_bounded_moves1(board, (5, 4))
print(make_readable(board1))

#peices can be bounded by 2 things, the first is a piece being in the way (the knight is the exception to this bound)
#the second bound a piece might be pinned (this can be handled later close to finishing game mechanics)

#plan to set bound 1: create a distance variable for each move, and direction variable, 
#if a piece in the way then all moves same direction with a bigger distance will no longer be a move
#if this piece is enemy then replace with 'k ' else replace with '  ' 
#this will have to be on a seperate board so it doesnt replace piece