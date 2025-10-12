import chess

if __name__ == "__main__":
    
    board = chess.Board()
    board.push_san('e4')
    legal_moves_lst = [board.san(m) for m in board.legal_moves]

    print('a5' in legal_moves_lst)

    import csv
import re
import argparse
import chess
from typing import TypedDict

class Position(TypedDict):
    id: int
    fen_position: str

class Move(TypedDict):
    id: int
    fen_id: int
    new_fen_id: int
    move: str
    white: int
    black: int
    draw: int

# Start with moves like e3 e4...

# For each position in a game convert the PGN data up to that point into a FEN board, get the next move.
# Look into the database for this FEN, if it is found add to the total for WHITE, BLACK, or DRAW by 1
# If it is not found in the database then add the FEN position to the database with a 1 for the outcome, 
# and 0's for the non-outcomes

import re
from typing import Tuple
from database import get_position_by_fen, insert_position, insert_move, get_move_by_fen_id_and_new_fen_id, update_move

def transform_game(movetext: str) -> Tuple[str, str]:
    """
    Clean up PGN / move-text for parsing.
    Removes tag header lines, {...} comments, move numbers, and result tokens.
    Returns:
        (cleaned_moves, result)
        - cleaned_moves: single-line cleaned string of tokens (suitable for PGN parsing or UCI/SAN fallbacks)
        - result: one of '1-0', '0-1', '1/2-1/2', '*', or '' if not found
    """
    if not movetext:
        return "", ""

    s = movetext.strip()

    # Capture result tokens (standard PGN endings)
    match = re.search(r"\b(1-0|0-1|1/2-1/2|\*)\b", s)
    result = match.group(1) if match else ""

    # Remove tag pairs like [Event "..." ] lines
    s = "\n".join(line for line in s.splitlines() if not line.strip().startswith("["))

    # Remove braces comments {...}
    s = re.sub(r"\{[^}]*\}", " ", s)

    # Remove move numbers like "1.", "1...", "12."
    s = re.sub(r"\d+\.+", " ", s)

    # Remove result tokens
    s = re.sub(r"\b(1-0|0-1|1/2-1/2|\*)\b", " ", s)

    # Collapse whitespace
    s = s.split()

    return s, result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="path to csv file where last or specified column is movetext (UCI/SAN/PGN)")
    args = p.parse_args()

    with open(args.csv, newline='', encoding="utf-8") as f:
        data = csv.reader(f)
        counter = 0
        illegal_games = 0
        for game_index, row in enumerate(data):
            if counter > 0:
                game = row[-2]
                opening = row[14]
                game, result = transform_game(game)
                board = chess.Board()

                for move_index, move_san in enumerate(game):
                    # Check move is legal
                    legal_moves = [board.san(m) for m in board.legal_moves]      
                    
                    if move not in legal_moves:
                        illegal_games += 1
                        break

                    # Either get move or its the first move in the first loop
                    pre_move_position: Position = get_position_by_fen(board.fen())

                    # Insert the starting board
                    if move_index == 0 and game_index == 1 and pre_move_position == None:
                        pre_move_position_id = insert_position(board.fen())

                    # Make move on board
                    board.push_san(move)

                    # Check that the new position is in the database
                    new_position_id = get_position_by_fen(board.fen())

                    # If the new postion not found in the database
                    if new_position_id == None:
                        new_position_id = insert_position(board.fen())
                    
                    white_result = 1 if result == '1-0' else 0
                    black_result = 1 if result == '0-1' else 0
                    draw_result = 1 if result == '1/2-1/2' else 0

                    # Check for the move, if not found insert
                    # If found update the move
                    move: Move = get_move_by_fen_id_and_new_fen_id(pre_move_position_id, new_position_id)

                    if move == None:
                        move_id = insert_move(pre_move_position_id, new_position_id, move_san, white_result, black_result, draw_result)
                    else:
                        update_move(
                            move.id, 
                            None if white_result == 0 else move.white + white_result,
                            None if black_result == 0 else move.black + black_result,
                            None if draw_result == 0 else move.draw + draw_result,
                        )

            counter += 1

            if counter > 2:
                break

        
if __name__ == "__main__":
    main()


    # Step 1: have the starting board in the database
    # Step 2: Make the move
    # Step 3: Make sure the new board is in the DB, if not then add it
    # Step 4: Add/update the move
