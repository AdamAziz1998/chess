
def array_coords_to_pygame_coords(array_coords):
    row, col = array_coords[0], array_coords[1]
    return ((80 * col + 40 - 25), 640 - (80 * row) - 25 + 40 - 80)

def pygame_coords_to_array_coords(pygame_coords):
    x, y = pygame_coords[0], pygame_coords[1]
    return (int((x + 25 - 40) / 80), int((640 - y + 25 - 40 + 80) / 80))
    
