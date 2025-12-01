def board_to_fen(board, active_color="w", castling="KQkq", en_passant="-", halfmove=0, fullmove=1):
    """
    Convert a 2D chess board array into a FEN string.

    :param board: 8x8 list of lists with:
                  'wP', 'wR', 'wN', 'wB', 'wQ', 'wK' for white pieces
                  'bP', 'bR', 'bN', 'bB', 'bQ', 'bK' for black pieces
                  None or "null" for empty squares
    :param active_color: "w" or "b"
    :param castling: castling availability string (e.g., "KQkq", "KQ", "-", etc.)
    :param en_passant: en passant target square (e.g., "e3", "-")
    :param halfmove: halfmove clock for 50-move rule
    :param fullmove: fullmove number
    :return: FEN string
    """
    fen_rows = []
    for row in board:
        empty_count = 0
        fen_row = ""
        for cell in row:
            if cell is None or cell == "null":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                color, piece = cell[0], cell[1]
                symbol = piece.upper() if color == "w" else piece.lower()
                fen_row += symbol
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)

    return f"{'/'.join(fen_rows)} {active_color} {castling} {en_passant} {halfmove} {fullmove}"


def fen_to_board(fen):
    """
    Convert a FEN string into a 2D chess board array + metadata.

    :param fen: FEN string
    :return: (board, active_color, castling, en_passant, halfmove, fullmove)
    """
    parts = fen.split()
    if len(parts) != 6:
        raise ValueError("Invalid FEN: must have 6 fields")

    rows, active_color, castling, en_passant, halfmove, fullmove = parts
    board = []
    for fen_row in rows.split("/"):
        row = []
        for char in fen_row:
            if char.isdigit():
                row.extend([None] * int(char))
            else:
                color = "w" if char.isupper() else "b"
                piece = char.upper()
                row.append(color + piece)
        board.append(row)

    return board, active_color, castling, en_passant, int(halfmove), int(fullmove)


# Example usage:

board = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
]

fen = board_to_fen(board, active_color="w", castling="KQkq", en_passant="-", halfmove=0, fullmove=1)
print("Board → FEN:", fen)

board_back, active, castling, ep, halfmove, fullmove = fen_to_board(fen)
print("FEN → Board:", board_back)
print("Extra info:", active, castling, ep, halfmove, fullmove)
