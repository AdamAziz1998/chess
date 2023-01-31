import itertools

def array_coords_to_pygame_coords_circle(array_coords):
    row, col = array_coords[0], array_coords[1]
    return ((80 * col + 40 - 12), 640 - (80 * row) - 12 + 40 - 80)

def array_coords_to_pygame_coords_kill_circle(array_coords):
    row, col = array_coords[0], array_coords[1]
    return ((80 * col + 40 - 20), 640 - (80 * row) - 20 + 40 - 80)

#this converts array_indexing into game coordinates, this is purely for piece placement
def array_coords_to_pygame_coords(array_coords):
    row, col = array_coords[0], array_coords[1]
    return ((80 * col + 40 - 25), 640 - (80 * row) - 25 + 40 - 80)

# the 2 functions below find out which square on the board was clicked in-game
def all_center_coords():
    vals = [(80*i) + 40 for i in range(8)]
    combs = [p for p in itertools.product(vals, repeat=2)]

    return combs

def find_closest_center_to_click(all_center_coords, clicked_coords):
    distances = []
    for k in range(len(all_center_coords)):
        d = ((clicked_coords[0] - all_center_coords[k][0])**2 + (clicked_coords[1] - all_center_coords[k][1])**2)**0.5
        distances.append(d)
    
    d_min_index = distances.index(min(distances))

    return all_center_coords[d_min_index]

#function below will convert the coordinate of the center of a square 
# to board index
def coord_to_index(coord):
    return (int(7 - (coord[1] - 40)/80), int((coord[0] - 40)/80))