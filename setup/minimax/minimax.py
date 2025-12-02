import chess
import math
from typing import Optional, Tuple

class MiniMaxEngine:
    """
    A simple chess engine implementing Minimax with Alpha-Beta pruning,
    Quiescence search, and basic Adaptive Deepening.
    """

    MATE_SCORE = 10**6
    
    # Moved out of the function to prevent re-creation on every call (Optimization)
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    def __init__(self, depth: int = 4):
        """
        Initialize the engine with a specific search depth.
        """
        self.max_depth = depth

    def get_best_move(self, board: chess.Board) -> Tuple[Optional[chess.Move], int]:
        """
        Calculates the best move for the current board state.
        Returns: (best_move, score)
        """
        best_move = None
        # Initialize best_eval based on whose turn it is
        best_eval = -math.inf if board.turn == chess.WHITE else math.inf
        
        # We need to preserve the board state, so we don't modify the object passed in
        # However, python-chess push/pop is safe if we match them perfectly.
        
        for move in board.legal_moves:
            board.push(move)
            # Call minimax with switched perspective (not board.turn)
            eval_score = self._minimax(board, self.max_depth - 1, -math.inf, math.inf, not board.turn)
            board.pop()

            if board.turn == chess.WHITE:
                if eval_score > best_eval:
                    best_eval = eval_score
                    best_move = move
            else:
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move

        return best_move, best_eval

    def _evaluate_board(self, board: chess.Board) -> int:
        """
        Static evaluation of the board position (Material Balance).
        """
        if board.is_checkmate():
            return -self.MATE_SCORE if board.turn else self.MATE_SCORE
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        # Improved efficiency by accessing class constant
        for piece_type, value in self.PIECE_VALUES.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
        return score

    def _quiescence(self, board: chess.Board, alpha: int, beta: int) -> int:
        """
        Quiescence search to handle 'noisy' positions (captures/checks) at the horizon.
        """
        stand_pat = self._evaluate_board(board)
        
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        for move in board.legal_moves:
            if board.is_capture(move) or board.gives_check(move):
                board.push(move)
                score = -self._quiescence(board, -beta, -alpha)
                board.pop()

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    def _minimax(self, board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
        """
        Minimax algorithm with Alpha-Beta pruning and Adaptive Deepening.
        """
        if depth == 0 or board.is_game_over():
            return self._quiescence(board, alpha, beta)

        if maximizing:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)
                
                # Adaptive deepening logic
                # Note: legal_moves.count() can be expensive; used sparingly
                extra_depth = 1 if board.is_check() or board.legal_moves.count() < 4 else 0
                
                eval_score = self._minimax(board, depth - 1 + extra_depth, alpha, beta, False)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                
                extra_depth = 1 if board.is_check() or board.legal_moves.count() < 4 else 0
                
                eval_score = self._minimax(board, depth - 1 + extra_depth, alpha, beta, True)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval