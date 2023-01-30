#to move i is to move up and down
# to move j is to move left and right


#white pawns will start on the second list in the array which will have coordinates (1, j)
def white_pawn_moves_unbounded(location_index):
    moves = []

    i, j = location_index

    kill_move1 = (i + 1, j + 1)
    kill_move2 = (i + 1, j - 1)
    move3 = (i + 1, j)

    moves.append(move3)
    if j == 0:
        moves.append(kill_move1)
    elif j == 7:
        moves.append(kill_move2)
    else:
        moves.append(kill_move1)
        moves.append(kill_move2)

    return moves


#black pawns will start on the second to last list in the array which will have coordinates (6, j)
def black_pawn_moves_unbounded(location_index):
    moves = []

    i, j = location_index

    kill_move1 = (i - 1, j + 1)
    kill_move2 = (i - 1, j - 1)
    move3 = (i - 1, j)

    moves.append(move3)

    if j == 0:
        moves.append(kill_move1)
    elif j == 7:
        moves.append(kill_move2)
    else:
        moves.append(kill_move1)
        moves.append(kill_move2)

    return moves

def rook_moves_unbounded(location_index):
    moves = []

    i, j = location_index
    for k in range(8):
        if k != i:
            move = (k, j)
            moves.append(move)
    for k in range(8):
        if k != j:
            move = (i, k)
            moves.append(move)
    
    return moves

def bishop_moves_unbounded(location_index):
    moves = []

    i, j = location_index

    i2, j2 = location_index
    while i2 != 7 and i2 != 0 and j2 != 7 and j2 != 0:
        i2, j2 = i2 + 1, j2 + 1
        move = (i2, j2)
        moves.append(move)
    
    i2, j2 = location_index
    while i2 != 7 and i2 != 0 and j2 != 7 and j2 != 0:
        i2, j2 = i2 + 1, j2 - 1
        move = (i2, j2)
        moves.append(move)

    i2, j2 = location_index
    while i2 != 7 and i2 != 0 and j2 != 7 and j2 != 0:
        i2, j2 = i2 - 1, j2 + 1
        move = (i2, j2)
        moves.append(move)

    i2, j2 = location_index
    while i2 != 7 and i2 != 0 and j2 != 7 and j2 != 0:
        i2, j2 = i2 - 1, j2 - 1
        move = (i2, j2)
        moves.append(move)

    return moves

#the queen is a bishop and a rook in one
def queen_moves_unbounded(location_index):
    moves1 = bishop_moves_unbounded(location_index)
    moves2 = rook_moves_unbounded(location_index)

    return moves1 + moves2


def king_moves_unbounded(location_index):
    moves = []

    i, j = location_index

    if i == 0:
        r = range(0, 2)
    elif i == 7:
        r = range(-1, 1)
    else:
        r = range(-1, 2)

    if j == 0:
        r1 = range(0, 2)
    elif j == 7:
        r1 = range(-1, 1)
    else:
        r1 = range(-1, 2)

    for k in r:
        for k1 in r1:
            if k != 0 or k1 != 0:
                move = (i + k, j + k1)

                moves.append(move)
    
    return moves

def knight_moves_unbounded(location_index):
    i, j = location_index

    moves0 = [
        (i + 1, j + 2),
        (i - 1, j + 2),
        (i + 1, j - 2),
        (i - 1, j - 2),
        (i + 2, j + 1),
        (i - 2, j + 1),
        (i + 2, j - 1),
        (i - 2, j - 1)
    ]

    moves = []

    for move in moves0:
        if 8 not in move and 9 not in move and -1 not in move and -2 not in move:
            moves.append(move)
    
    return moves