import chess
import math
from typing import Optional, Tuple


class MiniMaxEngine:
    """
    A simple chess engine implementing Minimax with Alpha-Beta pruning
    and Quiescence search.
    """

    MATE_SCORE = 10**6

    # Moved out of the function to prevent re-creation on every call (Optimization)
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,
    }

    # Center squares for positional bonus
    CENTER_SQUARES = {chess.E4, chess.D4, chess.E5, chess.D5}
    EXTENDED_CENTER = {
        chess.C3,
        chess.D3,
        chess.E3,
        chess.F3,
        chess.C4,
        chess.F4,
        chess.C5,
        chess.F5,
        chess.C6,
        chess.D6,
        chess.E6,
        chess.F6,
    }

    def __init__(self, depth: int = 4):
        """
        Initialize the engine with a specific search depth.
        """
        self.max_depth = depth

    @staticmethod
    def get_best_move_from_fen(
        fen_string: str, depth: int = 4
    ) -> Tuple[Optional[str], int]:
        """
        Takes a FEN string, converts it to a chess.Board, and computes the best move.

        Args:
            fen_string: The FEN string (may be partial, containing only the 4 core fields).
            depth: The search depth for the MiniMax engine.

        Returns:
            A tuple of (best_move_uci_string, score). Returns (None, 0) if FEN is invalid.
        """

        # 1. Validate and complete the FEN string
        # A full FEN has 6 fields. We assume the user provides the first 4:
        # 1. Piece placement, 2. Active color, 3. Castling availability, 4. En passant target square
        fen_parts = fen_string.strip().split()

        # If less than 4 parts, it's definitely malformed for our use case.
        if len(fen_parts) < 4:
            print(
                f"Error: FEN string must contain at least 4 fields. Received {len(fen_parts)}."
            )
            return (None, 0)

        # Complete the FEN by adding the last two fields (half-move clock and full-move number)
        # We assume 0 and 1 as default values for the missing fields.
        if len(fen_parts) == 4:
            fen_parts.append("0")  # Half-move clock (for 50-move rule)
            fen_parts.append("1")  # Full-move number
            complete_fen = " ".join(fen_parts)
        else:
            complete_fen = fen_string.strip()

        # 2. Convert to chess.Board and check validity
        try:
            board = chess.Board(complete_fen)
        except ValueError:
            print(f"Error: The generated FEN '{complete_fen}' is not valid.")
            return (None, 0)

        # 3. Instantiate and run the engine
        engine = MiniMaxEngine(depth=depth)
        best_move_obj, score = engine.get_best_move(board)

        # 4. Format the output
        if best_move_obj:
            return best_move_obj.uci(), score
        else:
            # Game is over (Checkmate, Stalemate, etc.)
            return (None, engine._evaluate_board(board))

    def get_best_move(self, board: chess.Board) -> Tuple[Optional[chess.Move], int]:
        """
        Calculates the best move for the current board state.
        Returns: (best_move, score)
        """
        best_move = None
        is_white = board.turn == chess.WHITE
        best_eval = -math.inf if is_white else math.inf

        # Order moves to improve alpha-beta pruning (captures first)
        moves = self._order_moves(board)

        for move in moves:
            board.push(move)
            # After push, it's opponent's turn. If we were White (maximizing),
            # opponent is Black (minimizing), so maximizing=False
            eval_score = self._minimax(
                board, self.max_depth - 1, -math.inf, math.inf, not is_white
            )
            board.pop()

            if is_white:
                if eval_score > best_eval:
                    best_eval = eval_score
                    best_move = move
            else:
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move

        return best_move, best_eval

    def _order_moves(self, board: chess.Board) -> list:
        """
        Order moves to improve alpha-beta pruning efficiency.
        Captures and checks first, then center moves.
        """
        captures = []
        checks = []
        center_moves = []
        other_moves = []

        for move in board.legal_moves:
            if board.is_capture(move):
                captures.append(move)
            elif board.gives_check(move):
                checks.append(move)
            elif (
                move.to_square in self.CENTER_SQUARES
                or move.to_square in self.EXTENDED_CENTER
            ):
                center_moves.append(move)
            else:
                other_moves.append(move)

        return captures + checks + center_moves + other_moves

    def _evaluate_board(self, board: chess.Board) -> int:
        """
        Static evaluation of the board position (Material + Positional).
        """
        if board.is_checkmate():
            return -self.MATE_SCORE if board.turn else self.MATE_SCORE
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        # Material evaluation
        for piece_type, value in self.PIECE_VALUES.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        # Positional bonus for center control (small bonuses)
        for sq in self.CENTER_SQUARES:
            piece = board.piece_at(sq)
            if piece:
                bonus = 30 if piece.piece_type in (chess.PAWN, chess.KNIGHT) else 10
                score += bonus if piece.color == chess.WHITE else -bonus

        for sq in self.EXTENDED_CENTER:
            piece = board.piece_at(sq)
            if piece:
                bonus = 10 if piece.piece_type in (chess.PAWN, chess.KNIGHT) else 5
                score += bonus if piece.color == chess.WHITE else -bonus

        return score

    def _quiescence(
        self, board: chess.Board, alpha: int, beta: int, maximizing: bool
    ) -> int:
        """
        Quiescence search to handle 'noisy' positions (captures) at the horizon.
        """
        stand_pat = self._evaluate_board(board)

        if maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat

            for move in board.legal_moves:
                if board.is_capture(move):
                    board.push(move)
                    score = self._quiescence(board, alpha, beta, False)
                    board.pop()

                    if score >= beta:
                        return beta
                    if score > alpha:
                        alpha = score
            return alpha
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

            for move in board.legal_moves:
                if board.is_capture(move):
                    board.push(move)
                    score = self._quiescence(board, alpha, beta, True)
                    board.pop()

                    if score <= alpha:
                        return alpha
                    if score < beta:
                        beta = score
            return beta

    def _minimax(
        self, board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool
    ) -> int:
        """
        Minimax algorithm with Alpha-Beta pruning.
        """
        if depth == 0 or board.is_game_over():
            return self._quiescence(board, alpha, beta, maximizing)

        # Order moves for better pruning
        moves = self._order_moves(board)

        if maximizing:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.pop()

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
