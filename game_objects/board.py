from game_objects.pieces import (
    wk1,
    bk1,
    wq1,
    bq1,
    wr1, wr2,
    br1, br2,
    wkn1, wkn2,
    bkn1, bkn2,
    wb1, wb2,
    bb1, bb2,
    wp1, wp2, wp3, wp4, wp5, wp6, wp7, wp8, 
    bp1, bp2, bp3, bp4, bp5, bp6, bp7, bp8 
    
)

board = [['  ' for i1 in range(8)] for i in range(8)]

starting_board = [
    [wr1, wkn1, wb1, wq1, wk1, wb2, wkn2, wr2],
    [wp1, wp2, wp3, wp4, wp5, wp6, wp7, wp8],
    ['  ' for i in range(8)],
    ['  ' for i in range(8)],
    ['  ' for i in range(8)],
    ['  ' for i in range(8)],
    [bp1, bp2, bp3, bp4, bp5, bp6, bp7, bp8],
    [br1, bkn1, bb1, bq1, bk1, bb2, bkn2, br2]
    

]

def make_readable(board):
    for k in range(1, len(board) +1):
        printer = []
        row = board[-k]

        for k1 in range(len(board)):
            if type(row[k1]) == str:
                printer.append(row[k1])
            else:
                printer.append(row[k1].team + row[k1].type)
        
        print(printer, '\n')

    return 1

def make_readable_black_perspective(board):
    for k in range(1, len(board) +1):
        printer = []
        row = board[k]

        for k1 in range(len(board)):
            if type(row[k1]) == str:
                printer.append(row[k1])
            else:
                printer.append(row[k1].team + row[k1].type)
        
        print(printer, '\n')

    return 1