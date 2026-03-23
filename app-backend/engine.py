from minimax.minimax import MiniMaxEngine
from neuralNetwork.infer import neural_network_best_move
import chess
from lichess import get_most_popular_move


def fen_to_board(fen_input: str) -> chess.Board:
    return chess.Board(fen_input)


def is_tactical_position(board: chess.Board) -> bool:
    if board.is_check():
        return True

    # You have a move that gives check -> possible mating tactic
    for move in board.legal_moves:
        if board.gives_check(move):
            return True

    # Looking for captures of hanging pieces
    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            # If the opponent cannot recapture a piece of equal or higher value, this is forcing
            if not any(board.is_capture(m) for m in board.legal_moves):
                board.pop()
                return True
            board.pop()

    # Very few legal moves for opponent after YOUR quiet move = forcing line
    quiet_moves = 0
    for move in board.legal_moves:
        if not board.is_capture(move) and not board.gives_check(move):
            quiet_moves += 1
    if quiet_moves <= 2:
        return True

    return False


def should_use_minimax(fen_position: str, score: int, threshold: int = 150) -> bool:
    """
    Returns True if minimax should be used — meaning:
    1) position is tactically sharp (high risk/opportunity)
    2) AND a minimax search confirms it leads to a meaningful win/avoid loss
    """
    board = chess.Board(fen_position)

    if not is_tactical_position(board):
        return False  # no reason to go deep

    if abs(score) >= 20000:  # checkmate
        return True

    if board.turn == chess.WHITE and score >= threshold:
        return True  # good for white
    if board.turn == chess.BLACK and score <= -threshold:
        return True  # good for black

    # No meaningful benefit
    return False


async def best_move(fen_position: str):
    lichess_move = await get_most_popular_move(fen_position)
    if lichess_move:
        return lichess_move["move"]

    minimax_move, score = MiniMaxEngine.get_best_move_from_fen(fen_position)

    if should_use_minimax(fen_position, score):
        return minimax_move

    return neural_network_best_move(fen_position)


if __name__ == "__main__":
    import asyncio
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    print(asyncio.run(best_move(fen)))
