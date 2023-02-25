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
    bp1, bp2, bp3, bp4, bp5, bp6, bp7, bp8,
    Piece
    
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
wq2 = Piece('w', 'q', wq1.image, False, False)
wr3 = Piece('w', 'r', wr1.image, False, False)
bq2 = Piece('b', 'q', bq1.image, False, False)
wk2 = Piece('w', 'k', wk1.image, False, False)
bk2 = Piece('b', 'k', bk1.image, False, False)
sample_board = [
    [wq2 ,'  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ', wr3, bq2,'  ',wk2 ,'  '],
    ['  ','  ','  ','  ', bk2,'  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  ']
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



from game_objects.pieces import (
    wk2,
    bk2,
    wq2,
    bq2,
    wr3, wr4,
    br3, br4,
    wkn3, wkn4,
    bkn3, bkn4,
    wb3, wb4,
    bb3, bb4,
    wp9, wp12, wp13, wp14, wp15, wp16, wp10, wp11, 
    bp9, bp12, bp13, bp14, bp15, bp16, bp10, bp11)

donny_board = [
    [wr3 ,'  ','  ','  ',wb3 ,'  ',wr4 ,'  '][::-1],
    ['  ','  ',wp2 ,'  ',wk2 ,'  ','  ',wp1 ][::-1],
    ['  ','  ',wkn3,'  ','  ','  ','  ','  '][::-1],
    [wp12,'  ',bkn3,'  ',wp9 ,'  ','  ','  '][::-1],
    [bp12,wp11,bkn4,wp10,bp9 ,'  ',bp13,'  '][::-1],
    ['  ',bp11,'  ',bp10,'  ','  ','  ','  '][::-1],
    ['  ',bb3 ,bp1,'  ','  ','  ','  ',bp2][::-1],
    ['  ',bk2 ,br4 ,'  ','  ','  ','  ',br3 ][::-1]
]