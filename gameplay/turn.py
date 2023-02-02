#location_index is the current location of the piece
def make_move(board, piece_location_index, move_location_index):
    i, j = piece_location_index
    piece = board[i][j]

    if piece.move0:
        piece.move0 = False
        piece.move1 = True

    elif piece.move1:
        piece.move1 = False

    board[i][j] = '  '
    i1, j1 = move_location_index
    board[i1][j1] = piece

    return board

#team_move is either 'w' or 'b'
def turn(board, piece_location_index, move_location_index, team_move):
    board1 = make_move(board, piece_location_index, move_location_index)
    if team_move == 'w':
        team_move = 'b'
    else:
        team_move = 'w'
    
    return board1, team_move




def checkmate_checker(board):
    pass

def stale_mate_checker(board):
    pass

def draw_checker(board):
    pass