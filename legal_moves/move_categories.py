def distance(move, location_index):
    i, j = location_index
    i1, j1 = move
    euclid_distance = ((i - i1)**2 + (j - j1)**2)**0.5

    if round(euclid_distance) != euclid_distance:
        vector_distance = round(euclid_distance / (2**0.5))
    else:
        vector_distance = euclid_distance
    return vector_distance

def direction(move, location_index):
    i, j = location_index
    i1, j1 = move

    #left up diagonal
    if i < i1 and j > j1:
        dir = 'lud'

    #right up diagonal
    elif i < i1 and j < j1:
        dir = 'rud'

    #left down diagonal
    elif i > i1 and j > j1:
        dir = 'ldd'

    #right down diagonal
    elif i > i1 and j < j1:
        dir = 'rdd'

    #left
    elif i == i1 and j > j1:
        dir = 'l'

    #right
    elif i == i1 and j < j1:
        dir = 'r'

    #up
    elif i < i1 and j == j1:
        dir = 'u'

    #down
    elif i > i1 and j == j1:
        dir = 'd'
    
    return dir

#move types are 'k' and 'x ' meaning kill move and move with no kill, 
# maybe will have 'p' for passant and 'c' for castle and 't' for when a pawn changes to a new piece at end of path
#direction consists of u for up d for down l for left r for right 
# and a combination of the previous ending with d representing a diagonal movement for example dld meaning down-left diagonal
class Move:
    def __init__(self, org_location: tuple, location_index: tuple, type: str, distance: float, direction: str):
        self.org_location = org_location
        self.location_index = location_index
        self.type = type
        self.distance = distance
        self.direction = direction