import re
import chess
from typing import Tuple, List, Dict, Set


def transform_game_batch(lines: List[str]) -> Tuple[Set[str], Dict[Tuple[str, str], Dict]]:
    """
    Parses a batch of raw CSV lines into FENs and aggregated move counts.
    Returns: (unique_fens_set, aggregated_moves_dict)
    """
    local_fens = set()
    # Key: (fen_before, fen_after) -> Val: {san: str, w: int, b: int, d: int}
    local_moves = {}

    for movetext in lines:
        if not movetext:
            continue

        # 1. Regex Cleanup (Combined into one pass for speed)
        text = re.sub(r'\[.*?\]|\{.*?\}|\d+\.+', ' ', movetext)

        # Extract Result
        match = re.search(r"(1-0|0-1|1/2-1/2)", text)
        result = match.group(1) if match else "*"

        # Clean moves list
        move_list = re.sub(r"(1-0|0-1|1/2-1/2|\*)", " ", text).split()

        w = 1 if result == "1-0" else 0
        b = 1 if result == "0-1" else 0
        d = 1 if result == "1/2-1/2" else 0

        # 2. Chess Logic
        board = chess.Board()
        for m_san in move_list:
            try:
                fen_before = board.epd()
                move = board.parse_san(m_san)
                board.push(move)
                fen_after = board.epd()

                local_fens.add(fen_before)
                local_fens.add(fen_after)

                # Use Tuple as Key
                key = (fen_before, fen_after)
                if key not in local_moves:
                    local_moves[key] = {"san": m_san, "w": 0, "b": 0, "d": 0}

                local_moves[key]["w"] += w
                local_moves[key]["b"] += b
                local_moves[key]["d"] += d
            except:
                # If a move is illegal, we stop processing this specific game
                break

    return local_fens, local_moves