import sys
sys.path.append('../CHESS')

from game_objects.board import starting_board, sample_board
from legal_moves.legal import king_side_castling, queen_side_castling, king_find, legal_moves
from chess_bot.chess_models import all_potential_moves
import requests
from stockfish import Stockfish

def coords_to_chess_loc(coords):
    x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    y = ['1', '2', '3', '4', '5', '6', '7', '8']
    return x[coords[1]] + y[coords[0]]

def chess_loc_to_coords(chess_loc):
    x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    y = ['1', '2', '3', '4', '5', '6', '7', '8']
    return y.index(chess_loc[1]), x.index(chess_loc[0])

#peice_placemtn data needs doing
def board_to_FEN(board, TEAM, all_moves, half_move, full_move):

    FEN_board = ''
    for k in range(1, 9):
        l = []
        for k1 in range(8):
            if board[-k][k1] == '  ' and (len(l) == 0 or type(l[-1]) != int):
                l.append(1)
            elif board[-k][k1] == '  ' and type(l[-1]) == int:
                l[-1] = l[-1] + 1
            else:
                if board[-k][k1].team == 'w':
                    l.append(board[-k][k1].type.capitalize())
                else:
                    l.append(board[-k][k1].type)

        FEN_board += ''.join([str(k2) for k2 in l]) + '/'

    active_piece = TEAM

    passant = '-'
    for m in all_moves:
        if m.type == 'p':
            passant = coords_to_chess_loc(m.location_index)
            

    w_king = king_find(board, 'w')
    b_king = king_find(board, 'b')

    wkc = 'K' if king_side_castling(board, board[w_king[0]][w_king[1]]) else ''
    wqk = 'Q' if queen_side_castling(board, board[w_king[0]][w_king[1]]) else ''
    bkc = 'k' if king_side_castling(board, board[b_king[0]][b_king[1]]) else ''
    bqk = 'q' if queen_side_castling(board, board[b_king[0]][b_king[1]])else ''
    castle = wkc + wqk + bkc + bqk

    if castle == '':
        castle = '-'

    FEN = ' '.join([FEN_board[:-1] , active_piece, castle, passant, str(half_move), str(full_move)])
    return FEN

def FEN_to_url(FEN):
    url = FEN.replace(' ', '%20')
    url1 = 'https://www.chessdb.cn/cdb.php?action=querybest&board='
    return url1 + url

def engine_move(board, TEAM, half_move_count, move_count):

    all_moves = all_potential_moves(board, TEAM)

    FEN = board_to_FEN(board, TEAM, all_moves, 0, 0)
    url = FEN_to_url(FEN)
    response = requests.get(url).text
    print(response)

    move_org_loc = chess_loc_to_coords(response.split(':')[1][:2])
    move_loc = chess_loc_to_coords(response.split(':')[1][2:])
    l_moves = legal_moves(board, move_org_loc)
    ai_move = 'something went wrong'
    for m in l_moves:
        if m.org_location == move_org_loc and m.location_index == move_loc:
            ai_move = m

    return ai_move

#this uses the stockfish engine downloaded online to find the best move
def engine_move1(board, TEAM, half_move_count, move_count):
    stockfish = Stockfish(path = '/opt/homebrew/Cellar/stockfish/15.1/bin/stockfish')

    all_moves = all_potential_moves(board, TEAM)
    FEN = board_to_FEN(board, TEAM, all_moves, half_move_count, move_count)

    if stockfish.is_fen_valid(FEN):
        stockfish.set_fen_position(FEN)
        best_move = stockfish.get_best_move()
        move_org_loc = chess_loc_to_coords(best_move[:2])
        move_loc = chess_loc_to_coords(best_move[2:])
        l_moves = legal_moves(board, move_org_loc)
        ai_move = 'something went wrong'
        for m in l_moves:
            if m.org_location == move_org_loc and m.location_index == move_loc:
                ai_move = m

        return ai_move

    else:
        return 'non valid FEN'