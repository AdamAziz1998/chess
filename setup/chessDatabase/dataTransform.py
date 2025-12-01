import csv
import re
import argparse
import chess
import logging
from typing import Tuple, Optional
from tqdm import tqdm

from database import Database


# ---------------------------
# Logging Setup
# ---------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------
# Data Models
# ---------------------------

class Position(dict):
    id: int
    fen_position: str


class Move(dict):
    id: int
    fen_id: int
    new_fen_id: int
    move: str
    white: int
    black: int
    draw: int


# ---------------------------
# Helpers
# ---------------------------

def transform_game(movetext: str) -> Tuple[list[str], str]:
    """
    Clean up PGN/move-text for parsing.

    Removes:
      - Tag header lines (e.g. [Event "..."])
      - Braced comments {...}
      - Move numbers like '1.', '1...'
      - Result tokens (1-0, 0-1, 1/2-1/2, *)

    Returns:
        moves   : list of SAN moves (as strings)
        result  : '1-0', '0-1', '1/2-1/2', '*', or '' if not found
    """
    if not movetext:
        return [], ""

    text = movetext.strip()

    # Extract game result
    match = re.search(r"\b(1-0|0-1|1/2-1/2|\*)\b", text)
    result = match.group(1) if match else ""

    # Remove PGN headers
    text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("["))

    # Remove comments {...}
    text = re.sub(r"\{[^}]*\}", " ", text)

    # Remove move numbers like "1." or "34..."
    text = re.sub(r"\d+\.+", " ", text)

    # Remove results
    text = re.sub(r"\b(1-0|0-1|1/2-1/2|\*)\b", " ", text)

    # Normalize whitespace → tokens
    moves = text.split()

    return moves, result


# ---------------------------
# Main Processing
# ---------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file where movetext (UCI/SAN/PGN) is in the last or specified column",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level (default: INFO)",
    )
    args = parser.parse_args()

    # Adjust logging level from CLI
    logger.setLevel(getattr(logging, args.log_level.upper()))

    logger.info("Starting PGN -> DB import")
    logger.info(f"Reading CSV: {args.csv}")

    with Database() as db:
        db.create_tables()
        illegal_games = 0
        batch_moves = []

        with open(args.csv, newline="", encoding="utf-8") as f:
            data = csv.reader(f)
            next(data)
            illegal_games = 0
            
            # Skip header row, wrap games in tqdm progress bar
            for game_index, row in enumerate(tqdm(data, desc="Processing games")):
                try:
                    movetext = row[-2]  # adjust column if needed
                    opening = row[14]   # unused for now, maybe store later?

                    moves, result = transform_game(movetext)
                    board = chess.Board()

                    for move_index, move_san in enumerate(moves):
                        # Validate move is legal
                        try:
                            move = board.parse_san(move_san) 
                            if move not in board.legal_moves:
                                illegal_games += 1
                                logger.debug(f"Illegal move '{move_san}' at game {game_index}, skipping game")
                                break
                        except ValueError:
                            illegal_games += 1
                            logger.debug(f"Invalid SAN '{move_san}' at game {game_index}, skipping game")
                            break
                        

                        # Current position before move
                        pre_position_id = db.get_position_id(board.fen())

                        # Make move
                        board.push_san(move_san)

                        # New position after move
                        new_position_id = db.get_position_id(board.fen())

                        # Outcome flags
                        white_result = 1 if result == "1-0" else 0
                        black_result = 1 if result == "0-1" else 0
                        draw_result = 1 if result == "1/2-1/2" else 0

                        # Insert or update move record
                        db.insert_move(pre_position_id, new_position_id, move_san, white_result, black_result, draw_result)

                except Exception as e:
                    logger.error(f"Error processing game {game_index}: {e}", exc_info=True)
                    db.rollback()
                
                if game_index == 1000:
                    break

    logger.info(f"Finished processing {game_index} games")
    logger.warning(f"Illegal games skipped: {illegal_games}")


# ---------------------------
# Entry Point
# ---------------------------

if __name__ == "__main__":
    main()