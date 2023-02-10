from game_objects.pieces import wr, br, Piece

#location_index is the current location of the piece
def make_move(baord_array, piece_location_index, move_location_index, move, pawn_transform_piece):
    i, j = piece_location_index
    piece = baord_array[i][j]

    if piece.move0:
        piece.move0 = False
        piece.move1 = True

    elif piece.move1:
        piece.move1 = False

    baord_array[i][j] = '  '
    i1, j1 = move_location_index
    baord_array[i1][j1] = piece

    if move.type == 'p':
        baord_array[i][j1] = '  '
    
    elif move.type == 'kc':
        baord_array[i][7] = '  '
        if i == 0:
            baord_array[i][5] = Piece('w', 'r', wr.image, False, False)
        else:
            baord_array[i][5] = Piece('b', 'r', wr.image, False, False)
    
    if move.type == 'qc':
        
        baord_array[i][0] = '  '
        if i == 0:
            baord_array[i][3] = Piece('w', 'r', wr.image, False, False)
        else:
            baord_array[i][3] = Piece('b', 'r', wr.image, False, False)
    
    #this will be false unless the move is the pawn reaching the end of the file, and the pawn_transform input will be
    #  the piece that the pawn transforms into
    if pawn_transform_piece:
        baord_array[i1][j1] = pawn_transform_piece

    return baord_array

#team_move is either 'w' or 'b'
# pawn_transform_piece will hold the piece that the pawn will trnasform to
def turn(board_array, piece_location_index, move_location_index, team_move, move, pawn_transform_piece):
    board_array1 = make_move(board_array, piece_location_index, move_location_index, move, pawn_transform_piece)
    if team_move == 'w':
        team_move = 'b'
    else:
        team_move = 'w'
    
    return board_array1, team_move


def checkmate_checker(board_array):
    pass

def stale_mate_checker(board_array):
    pass

def draw_checker(board_array):
    pass