#!/usr/bin/env python3
import io
import os
import csv
import re
import json
import argparse
import logging
import sys

import chess
import chess.pgn
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

logging.basicConfig(
    level=logging.DEBUG,
    format="%(processName)s: %(message)s",
    stream=sys.stdout
)

# ------------------
# Helpers
# ------------------

def transform_game(movetext: str) -> str:
    """
    Clean up PGN / move-text for parsing.
    Removes tag header lines, {...} comments, move numbers, and result tokens.
    Returns a single-line cleaned string of tokens (suitable for PGN parsing or UCI/SAN fallbacks).
    """
    if not movetext:
        return ""

    s = movetext.strip()

    # Remove tag pairs like [Event "..." ] lines
    s = "\n".join(line for line in s.splitlines() if not line.strip().startswith("["))

    # Remove braces comments {...}
    s = re.sub(r"\{[^}]*\}", " ", s)

    # Remove move numbers like "1.", "1...", "12."
    s = re.sub(r"\d+\.+", " ", s)

    # Remove result tokens
    s = re.sub(r"\b(1-0|0-1|1/2-1/2|\*)\b", " ", s)

    # Collapse whitespace
    s = " ".join(s.split())
    return s


def board_to_matrix_uint8(board: chess.Board):
    """
    Convert board to (13,8,8) uint8 tensor.
    Channels 0-5: white pawn..king
    Channels 6-11: black pawn..king
    Channel 12: legal targets (to-squares) for the side to move

    NOTE: Using row = 7 - rank so row 0 corresponds to rank 8 (visual top).
    If your training code expects a different orientation, change the row mapping accordingly.
    """
    mat = np.zeros((13, 8, 8), dtype=np.uint8)
    for square, piece in board.piece_map().items():
        rank = chess.square_rank(square)   # 0..7 where 0 is rank 1
        file = chess.square_file(square)   # 0..7 where 0 is file a
        row = 7 - rank
        col = file
        piece_type = piece.piece_type - 1  # 0..5
        piece_color_offset = 0 if piece.color else 6
        mat[piece_type + piece_color_offset, row, col] = 1

    for move in board.legal_moves:
        to_sq = move.to_square
        r = 7 - chess.square_rank(to_sq)
        c = chess.square_file(to_sq)
        mat[12, r, c] = 1

    return mat


PROM_OFFSET = 4096
def move_to_index(move: chess.Move):
    """
    Map (from,to, optional promotion) to unique integer in [0, 20479].
    Matches your original scheme: base = from*64 + to, promotions appended after PROM_OFFSET.
    """
    base = move.from_square * 64 + move.to_square
    if move.promotion is None:
        return base
    prom_map = {chess.KNIGHT: 0, chess.BISHOP: 1, chess.ROOK: 2, chess.QUEEN: 3}
    prom_idx = prom_map.get(move.promotion, 0)
    return PROM_OFFSET + base * 4 + prom_idx


def process_game(mvtext: str):
    """
    Robust processing:
      - Cleans text
      - Tries PGN parsing (chess.pgn.read_game)
      - Fallback: token-based UCI parsing (e2e4) and SAN parsing
    Returns (X_stack, y_array) or None on failure.
    """
    if not mvtext:
        return None

    mvtext = transform_game(mvtext)
    if not mvtext:
        return None

    # Try PGN parsing first
    try:
        pgn = io.StringIO(mvtext)
        game = chess.pgn.read_game(pgn)
    except Exception:
        game = None

    # If PGN parsed successfully, use mainline_moves()
    if game is not None:
        board = game.board()
        X_list, y_list = [], []
        for move in game.mainline_moves():
            # skip illegal moves (defensive)
            if move not in board.legal_moves:
                logging.debug("Encountered illegal move in PGN: %s", move)
                return None
            X_list.append(board_to_matrix_uint8(board))
            y_list.append(move_to_index(move))
            board.push(move)

        if not X_list:
            return None
        return np.stack(X_list), np.array(y_list, dtype=np.int32)

    # Fallback: assume space-separated UCI tokens (or SAN tokens)
    board = chess.Board()
    X_list, y_list = [], []
    tokens = mvtext.split()
    for tok in tokens:
        move = None
        tok_lower = tok.lower()

        # quick UCI pattern check: e2e4 or e7e8q
        if re.fullmatch(r"[a-h][1-8][a-h][1-8][qrbn]?", tok_lower):
            try:
                move = chess.Move.from_uci(tok_lower)
            except Exception:
                move = None

        # try SAN if UCI failed
        if move is None:
            try:
                move = board.parse_san(tok)
            except Exception:
                # cannot parse this token
                logging.debug("Cannot parse token as UCI or SAN: %s", tok)
                return None

        if move not in board.legal_moves:
            logging.debug("Parsed move not legal at this position: %s", move)
            return None

        X_list.append(board_to_matrix_uint8(board))
        y_list.append(move_to_index(move))
        board.push(move)

    if not X_list:
        return None
    return np.stack(X_list), np.array(y_list, dtype=np.int32)


# ------------------
# Main
# ------------------

def mv_generator(path, moves_col, rows_limit):
    """Yield move-text strings from CSV (skips first row as header)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        # skip header (safe even if there isn't one: first row will be skipped)
        _ = next(reader, None)
        for i, row in enumerate(reader):
            if rows_limit and i >= rows_limit:
                break
            try:
                yield row[moves_col] if moves_col is not None else row[-1]
            except Exception:
                continue

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="path to csv file where last or specified column is movetext (UCI/SAN/PGN)")
    p.add_argument("--out_dir", default="./processed", help="output folder")
    p.add_argument("--moves_col", type=int, default=None, help="index of moves column (0-based). If omitted uses last column")
    p.add_argument("--rows_limit", type=int, default=None, help="optional: only process first N rows of CSV (excluding header)")
    p.add_argument("--batch_size", type=int, default=10000, help="how many samples to buffer before writing to disk (NOT used to limit memory in this version)")
    p.add_argument("--workers", type=int, default=cpu_count(), help="number of parallel workers")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Count rows (using csv.reader to be robust to quoted newlines)
    print("Counting rows (this assumes a header row will be skipped)...")
    with open(args.csv, newline="", encoding="utf-8") as f:
        total_lines = sum(1 for _ in csv.reader(f))
    # assume first row is header -> games = total_lines - 1
    total_games = max(0, total_lines - 1)
    if args.rows_limit:
        total_games = min(total_games, args.rows_limit)
    print(f"Games to process (excluding header): {total_games}")

    X_batches, y_batches = [], []
    total_positions = 0
    counter_none = 0

    # Use a context manager to ensure pool closes cleanly
    with Pool(args.workers) as pool:
        mv_iter = mv_generator(args.csv, args.moves_col, args.rows_limit)
        print("Processing games in parallel...")
        for result in tqdm(pool.imap_unordered(process_game, mv_iter, chunksize=10), total=total_games):
            if result is None:
                counter_none += 1
                continue
            X_arr, y_arr = result
            X_batches.append(X_arr)
            y_batches.append(y_arr)
            total_positions += len(y_arr)

    print("Games skipped / failed:", counter_none)
    print(f"Total positions: {total_positions}")

    if total_positions == 0:
        print("No positions collected, exiting.")
        return

    # Allocate memmaps
    X_path = os.path.join(args.out_dir, "X.dat")
    y_path = os.path.join(args.out_dir, "y.dat")
    meta_path = os.path.join(args.out_dir, "meta.json")

    X_mem = np.memmap(X_path, dtype=np.uint8, mode="w+", shape=(total_positions, 13, 8, 8))
    y_mem = np.memmap(y_path, dtype=np.int32, mode="w+", shape=(total_positions,))

    # Write in order
    idx = 0
    for X_arr, y_arr in zip(X_batches, y_batches):
        n = len(y_arr)
        X_mem[idx:idx+n] = X_arr
        y_mem[idx:idx+n] = y_arr
        idx += n

    X_mem.flush()
    y_mem.flush()

    meta = {
        "n_samples": int(total_positions),
        "x_path": X_path,
        "y_path": y_path,
        "dtype_x": "uint8",
        "dtype_y": "int32",
        "shape_x": [total_positions, 13, 8, 8],
        "shape_y": [total_positions],
        "num_classes": 20480,
    }
    with open(meta_path, "w", encoding="utf-8") as mf:
        json.dump(meta, mf)

    print("Done. Meta written to", meta_path)

if __name__ == "__main__":
    main()
