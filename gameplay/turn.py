from game_objects.pieces import wr, br, Piece

#location_index is the current location of the piece
def make_move(board_array, piece_location_index, move_location_index, move, pawn_transform_piece):
    i, j = piece_location_index
    piece = board_array[i][j]

    if piece.move0:
        piece.move0 = False
        piece.move1 = True

    elif piece.move1:
        piece.move1 = False

    board_array[i][j] = '  '
    i1, j1 = move_location_index
    board_array[i1][j1] = piece

    if move.type == 'p':
        board_array[i][j1] = '  '
    
    elif move.type == 'kc':
        board_array[i][7] = '  '
        if i == 0:
            board_array[i][5] = Piece('w', 'r', wr.image, False, False)
        else:
            board_array[i][5] = Piece('b', 'r', wr.image, False, False)
    
    if move.type == 'qc':
        
        board_array[i][0] = '  '
        if i == 0:
            board_array[i][3] = Piece('w', 'r', wr.image, False, False)
        else:
            board_array[i][3] = Piece('b', 'r', wr.image, False, False)
    
    #this will be false unless the move is the pawn reaching the end of the file, and the pawn_transform input will be
    #  the piece that the pawn transforms into
    if pawn_transform_piece:
        board_array[i1][j1] = pawn_transform_piece

    return board_array

#team_move is either 'w' or 'b'
# pawn_transform_piece will hold the piece that the pawn will trnasform to
def turn(board_array, piece_location_index, move_location_index, team_move, move, pawn_transform_piece, kill):
    if type(board_array[move_location_index[0]][move_location_index[1]]) != str:
        kill = 0
    else:
        kill += 1
    
    board_array1 = make_move(board_array, piece_location_index, move_location_index, move, pawn_transform_piece)
    if team_move == 'w':
        team_move = 'b'
    else:
        team_move = 'w'
            
    return board_array1, team_move, kill