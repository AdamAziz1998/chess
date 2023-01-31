import sys
sys.path.append('../CHESS')

from game_objects.board import board

#location_index is the current location of the piece
def make_move(board, piece_location_index, move_location_index):
    i, j = piece_location_index
    piece = board[i][j]
    board[i][j] = '  '
    i1, j1 = move_location_index
    board[i1][j1] = piece
    return board