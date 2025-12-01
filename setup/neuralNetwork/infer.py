import torch
import torch.nn.functional as F
import chess
import numpy as np
from .model import ChessModel

# ----- Constants -----
PROM_OFFSET = 4096  # must match your training encoding scheme
NUM_CLASSES = 20480  # from meta.json

# ----- Load model once -----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = ChessModel(num_classes=NUM_CLASSES).to(device)
_model.load_state_dict(torch.load("chess_model.pt", map_location=device))
_model.eval()

# ----- FEN → (13, 8, 8) encoding (matches csv_to_memmap.py) -----
def board_to_matrix_uint8(board: chess.Board):
    mat = np.zeros((13, 8, 8), dtype=np.uint8)
    for square, piece in board.piece_map().items():
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        row = 7 - rank
        col = file
        piece_type = piece.piece_type - 1
        piece_color_offset = 0 if piece.color else 6
        mat[piece_type + piece_color_offset, row, col] = 1
    for move in board.legal_moves:
        to_sq = move.to_square
        r = 7 - chess.square_rank(to_sq)
        c = chess.square_file(to_sq)
        mat[12, r, c] = 1
    return mat

# ----- Inverse of move_to_index -----
def index_to_move(index: int, board: chess.Board) -> chess.Move:
    """Inverse mapping of move_to_index"""
    if index < PROM_OFFSET:
        from_sq = index // 64
        to_sq = index % 64
        return chess.Move(from_sq, to_sq)

    # Promotion move
    idx = index - PROM_OFFSET
    base, prom_idx = divmod(idx, 4)
    from_sq = base // 64
    to_sq = base % 64
    prom_map = {0: chess.KNIGHT, 1: chess.BISHOP, 2: chess.ROOK, 3: chess.QUEEN}
    return chess.Move(from_sq, to_sq, promotion=prom_map[prom_idx])

# ----- Core inference -----
@torch.no_grad()
def neural_network_best_move(fen: str) -> str:
    """Return best move in UCI format for a given FEN."""
    board = chess.Board(fen)
    x = torch.tensor(board_to_matrix_uint8(board), dtype=torch.float32).unsqueeze(0).to(device)
    logits = _model(x)
    probs = F.softmax(logits, dim=1)[0]

    # Rank indices by probability
    sorted_indices = torch.argsort(probs, descending=True)

    # Find first legal move
    for idx in sorted_indices.tolist():
        move = index_to_move(idx, board)
        if move in board.legal_moves:
            return move.uci()

    # Fallback (shouldn't happen)
    return "0000"

@torch.no_grad()
def infer_top_moves(fen: str, k: int = 5):
    """Return top-k legal moves with probabilities."""
    board = chess.Board(fen)
    x = torch.tensor(board_to_matrix_uint8(board), dtype=torch.float32).unsqueeze(0).to(device)
    logits = _model(x)
    probs = F.softmax(logits, dim=1)[0]

    sorted_indices = torch.argsort(probs, descending=True)

    results = []
    for idx in sorted_indices.tolist():
        move = index_to_move(idx, board)
        if move in board.legal_moves:
            results.append((move.uci(), float(probs[idx])))
        if len(results) >= k:
            break
    return results
