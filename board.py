from pieces import (
    wk,
    wq,
    wr,
    wkn,
    wb,
    wp,
    bk,
    bq,
    br,
    bkn,
    bb,
    bp
)

board = [['  ' for i1 in range(8)] for i in range(8)]

starting_board = [
    [br, bkn, bb, bq, bk, bb, bkn, br],
    [bp for i in range(8)],
    ['  ' for i in range(8)],
    ['  ' for i in range(8)],
    ['  ' for i in range(8)],
    ['  ' for i in range(8)],
    [wp for i in range(8)],
    [wr, wkn, wb, wq, wk, wb, wkn, wr]

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