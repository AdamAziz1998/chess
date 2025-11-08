import psycopg2
from minimaxAlgorithm.minimaxAlgo import minimax_best_move
from neuralNetwork.infer import neural_network_best_move
import chess
from chessDatabase.database import Database

def fen_to_board(fen: str) -> chess.Board:
    return chess.Board(fen)

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

def should_use_minimax(score, threshold: int = 150) -> bool | str:
    """
    Returns True if minimax should be used — meaning:
    1) position is tactically sharp (high risk/opportunity)
    2) AND a minimax search confirms it leads to a meaningful win/avoid loss
    """
    board = chess.Board(fen)

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

def best_move(fen: str):
    try:
        with Database() as db:
            chess_database_move = db.get_most_popular_move(fen)
    except psycopg2.OperationalError as e:
        print(f"\nDATABASE CONNECTION FAILED:")
        print(f"Please check your DB_SETTINGS in db_manager.py")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    if chess_database_move:
        return chess_database_move
    
    minimax_move, score = minimax_best_move(fen)

    if should_use_minimax(score):
        return minimax_move

    return neural_network_best_move(fen)

if __name__ == "__main__":
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    best_move(fen)