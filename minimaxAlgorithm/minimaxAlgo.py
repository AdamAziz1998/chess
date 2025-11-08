import chess
import math

MATE_SCORE = 10**6  # Arbitrary large value to represent mate
MAX_DEPTH = 4       # You can tune this for performance

# Evaluation function (still simple: material balance)
def evaluate_board(board: chess.Board) -> int:
    if board.is_checkmate():
        return -MATE_SCORE if board.turn else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    score = 0
    for piece_type, value in piece_values.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score

# Quiescence search: keep exploring captures/checks when position is "noisy"
def quiescence(board: chess.Board, alpha: int, beta: int) -> int:
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            board.push(move)
            score = -quiescence(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    return alpha

# Minimax with alpha-beta + quiescence + adaptive deepening
def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return quiescence(board, alpha, beta)

    if maximizing:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            # Adaptive deepening: if branch is "forcing" (few moves), search deeper
            extra_depth = 1 if board.is_check() or board.legal_moves.count() < 4 else 0
            eval = minimax(board, depth - 1 + extra_depth, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            extra_depth = 1 if board.is_check() or board.legal_moves.count() < 4 else 0
            eval = minimax(board, depth - 1 + extra_depth, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Get best move for a position
def minimax_best_move(fen: str, depth: int = MAX_DEPTH) -> chess.Move:
    board = chess.Board(fen)
    best_move = None
    best_eval = -math.inf if board.turn == chess.WHITE else math.inf

    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, -math.inf, math.inf, not board.turn)
        board.pop()

        if board.turn == chess.WHITE:
            if eval > best_eval:
                best_eval = eval
                best_move = move
        else:
            if eval < best_eval:
                best_eval = eval
                best_move = move

    return best_move, best_eval