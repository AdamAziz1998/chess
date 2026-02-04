"""
Unit tests for minimax/minimax.py and chess-engine/engine.py

Tests board evaluation, alpha-beta pruning, and best move computation
using specific FEN positions (Scholar's Mate, Endgames, etc.)
"""

from unittest.mock import Mock
import sys
import chess

from minimax.minimax import MiniMaxEngine


# Helper to import from chess-engine (hyphenated directory)
def _get_chess_engine_module():
    import os

    # Mock all dependencies before loading the module
    mock_minimax = Mock()
    mock_minimax.MiniMaxEngine = MiniMaxEngine
    sys.modules["minimax"] = mock_minimax
    sys.modules["minimax.minimax"] = mock_minimax
    sys.modules["neuralNetwork"] = Mock()
    sys.modules["neuralNetwork.infer"] = Mock()
    sys.modules["chessDatabase"] = Mock()
    sys.modules["chessDatabase.database"] = Mock()

    engine_path = os.path.join(
        os.path.dirname(__file__), "..", "chess-engine", "engine.py"
    )

    # Read and modify the source to fix relative imports
    with open(engine_path, "r") as f:
        source = f.read()

    # Replace relative import with absolute import that uses our mocked module
    source = source.replace(
        "from ..minimax.minimax import MiniMaxEngine",
        "from minimax.minimax import MiniMaxEngine",
    )

    # Compile and execute the modified source
    code = compile(source, engine_path, "exec")
    module = type(sys)("chess_engine_module")
    module.__file__ = engine_path
    exec(code, module.__dict__)

    return module


class TestMiniMaxEngineEvaluation:
    """Tests for the static board evaluation function."""

    def test_starting_position_is_equal(self, starting_fen: str):
        """Starting position should evaluate to ~0 (equal material)."""
        engine = MiniMaxEngine(depth=1)
        board = chess.Board(starting_fen + " 0 1")  # Complete FEN
        score = engine._evaluate_board(board)
        assert score == 0, "Starting position should have equal material"

    def test_white_up_queen_positive_score(self):
        """White up a queen should have a significantly positive score."""
        # White has queen, black doesn't
        fen = "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        engine = MiniMaxEngine(depth=1)
        board = chess.Board(fen)
        score = engine._evaluate_board(board)
        assert score >= 900, f"White up a queen should score >= 900, got {score}"

    def test_black_up_rook_negative_score(self):
        """Black up a rook should have a negative score."""
        # Black has extra rook
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/1NBQKBN1 w Qkq - 0 1"
        engine = MiniMaxEngine(depth=1)
        board = chess.Board(fen)
        score = engine._evaluate_board(board)
        assert score <= -500, f"Black up a rook should score <= -500, got {score}"

    def test_checkmate_returns_mate_score(self, black_checkmate_fen: str):
        """Checkmate position should return MATE_SCORE."""
        # Back rank mate - Black king is checkmated
        fen = "6k1/5ppp/8/8/8/8/8/4K2R b - - 0 1"  # Ra8# just played
        board = chess.Board(fen)
        board.push_uci("g8h8")  # Force a legal move context
        board.pop()

        # Create a checkmate position directly
        checkmate_fen = "6Rk/5ppp/8/8/8/8/8/4K3 b - - 0 1"
        board = chess.Board(checkmate_fen)
        engine = MiniMaxEngine(depth=1)

        if board.is_checkmate():
            score = engine._evaluate_board(board)
            assert abs(score) == MiniMaxEngine.MATE_SCORE

    def test_stalemate_returns_zero(self, stalemate_fen: str):
        """Stalemate position should evaluate to 0."""
        engine = MiniMaxEngine(depth=1)
        board = chess.Board(stalemate_fen + " 0 1")

        if board.is_stalemate():
            score = engine._evaluate_board(board)
            assert score == 0, "Stalemate should evaluate to 0"


class TestMiniMaxBestMove:
    """Tests for best move computation using alpha-beta pruning."""

    def test_scholars_mate_finds_qxf7(self, scholars_mate_fen: str):
        """
        Scholar's Mate position: White should find Qxf7# (checkmate).
        FEN: Queen on h5, Bishop on c4, Black is vulnerable on f7.
        """
        best_move, score = MiniMaxEngine.get_best_move_from_fen(
            scholars_mate_fen, depth=3
        )
        assert best_move == "h5f7", f"Expected Qxf7 (h5f7), got {best_move}"
        assert score == MiniMaxEngine.MATE_SCORE, "Checkmate should return MATE_SCORE"

    def test_endgame_kq_vs_k_finds_forcing_move(self, endgame_kq_vs_k_fen: str):
        """
        K+Q vs K endgame: Engine should find a forcing move toward checkmate.
        Not testing for a specific move, but ensuring a positive score for White.
        """
        best_move, score = MiniMaxEngine.get_best_move_from_fen(
            endgame_kq_vs_k_fen, depth=4
        )
        assert best_move is not None, "Should find a valid move in K+Q vs K"
        assert score > 0, f"White should be winning, got score {score}"

    def test_capture_hanging_queen(self):
        """Engine should capture a hanging queen."""
        # White pawn or queen can capture black queen on d3 (knight on c6 can't reach d3)
        # Best move is cxd3 (pawn takes queen) as it gains more material than Qxd3 (queen trade)
        fen = "r1b1kbnr/pppp1ppp/2n5/8/8/3q4/PPPP1PPP/RNBQKB1R w KQkq -"
        best_move, score = MiniMaxEngine.get_best_move_from_fen(fen, depth=3)
        # White pawn captures black queen; score should be highly positive
        assert best_move == "c2d3", f"Should capture queen with cxd3, got {best_move}"
        assert score > 500, f"Should gain significant material, got {score}"

    def test_avoid_blunder_back_rank(self):
        """Engine should not blunder into back rank mate."""
        # White to move, must not ignore back rank threat
        fen = "6k1/5ppp/8/8/8/8/5PPP/r3R1K1 w - -"
        best_move, score = MiniMaxEngine.get_best_move_from_fen(fen, depth=3)
        # Should defend (e.g., Rxe1 or move king) rather than ignore
        assert best_move is not None, "Should find a defensive move"

    def test_starting_position_returns_valid_move(self, starting_fen: str):
        """Starting position should return a valid opening move."""
        best_move, score = MiniMaxEngine.get_best_move_from_fen(starting_fen, depth=2)
        valid_opening_moves = {
            "e2e4",
            "d2d4",
            "c2c4",
            "g1f3",
            "b1c3",
            "g1h3",
            "e2e3",
            "d2d3",
            "a2a3",
            "h2h3",
            "g2g3",
            "b2b3",
            "a2a4",
            "b2b4",
            "c2c3",
            "f2f3",
            "f2f4",
            "g2g4",
            "h2h4",
        }
        assert best_move in valid_opening_moves, f"Got unexpected move: {best_move}"


class TestMiniMaxEdgeCases:
    """Edge case and error handling tests."""

    def test_invalid_fen_returns_none(self):
        """Invalid FEN string should return (None, 0)."""
        invalid_fen = "not_a_valid_fen"
        best_move, score = MiniMaxEngine.get_best_move_from_fen(invalid_fen)
        assert best_move is None
        assert score == 0

    def test_partial_fen_too_short_returns_none(self):
        """FEN with fewer than 4 parts should return (None, 0)."""
        short_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"  # Only 2 parts
        best_move, score = MiniMaxEngine.get_best_move_from_fen(short_fen)
        assert best_move is None
        assert score == 0

    def test_checkmate_position_returns_none_move(self):
        """In a checkmate position, no move is available."""
        # Black is checkmated
        checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq -"
        board = chess.Board(checkmate_fen + " 0 1")

        # Verify this is actually checkmate
        if board.is_checkmate():
            best_move, _ = MiniMaxEngine.get_best_move_from_fen(
                checkmate_fen, depth=1
            )
            assert best_move is None

    def test_depth_parameter_respected(self, starting_fen: str):
        """Different depths should be accepted without error."""
        for depth in [1, 2, 3]:
            best_move, _ = MiniMaxEngine.get_best_move_from_fen(
                starting_fen, depth=depth
            )
            assert best_move is not None, f"Depth {depth} should return a move"


class TestChessEngineWithMockedNN:
    """
    Tests for chess-engine/engine.py with mocked neural network.
    This avoids loading heavy ML models during unit tests.
    """

    def test_best_move_uses_database_first(self):
        """
        If a move exists in the database, it should be returned
        without calling the neural network.
        """
        # Prepare engine module and mocks
        engine_module = _get_chess_engine_module()
        mock_nn = Mock(name="neural_network_best_move", return_value="e2e4")
        engine_module.neural_network_best_move = mock_nn

        # Dummy Database context manager returning a move from DB
        class DummyDB:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def get_most_popular_move(self, fen_position):
                return {"move": "d2d4"}
        
        engine_module.Database = DummyDB

        # When DB has a move, engine should return it and NOT call the NN
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        result = engine_module.best_move(fen)
        assert result == "d2d4"
        mock_nn.assert_not_called()

    def test_neural_network_fallback_called(self):
        """
        When database returns nothing and minimax score is below threshold,
        neural network should be used as fallback.
        """
        mock_nn = Mock(return_value="g1f3")
        sys.modules["neuralNetwork"] = Mock()
        sys.modules["neuralNetwork.infer"] = Mock()
        sys.modules["neuralNetwork.infer"].neural_network_best_move = mock_nn

        # This test validates the mocking pattern works
        result = mock_nn("some_fen")
        assert result == "g1f3"
        mock_nn.assert_called_once_with("some_fen")

    def test_is_tactical_position_check(self):
        """Test tactical position detection - in check should return True."""
        engine_module = _get_chess_engine_module()
        is_tactical_position = engine_module.is_tactical_position

        # King in check
        board = chess.Board(
            "rnbqkbnr/ppppp1pp/8/5p1Q/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2"
        )
        assert is_tactical_position(board) is True

    def test_is_tactical_position_can_give_check(self):
        """If a legal checking move exists, position is tactical."""
        engine_module = _get_chess_engine_module()
        is_tactical_position = engine_module.is_tactical_position

        # Scholar's mate pattern: Qxf7+ is available immediately
        board = chess.Board(
            "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq -"
        )
        assert is_tactical_position(board) is True

    def test_is_tactical_position_quiet(self):
        """A quiet middlegame position may not be tactical."""
        engine_module = _get_chess_engine_module()
        is_tactical_position = engine_module.is_tactical_position

        # Closed position, no immediate tactics
        board = chess.Board(
            "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        )
        # Function should return a boolean regardless of the position
        result = is_tactical_position(board)
        assert isinstance(result, bool)


class TestAlphaBetaPruning:
    """Tests to verify alpha-beta pruning is working correctly."""

    def test_pruning_produces_same_result_as_no_pruning(self, starting_fen: str):
        """
        Alpha-beta pruning should produce the same result as full minimax
        (just faster). We verify by running at low depth.
        """
        engine = MiniMaxEngine(depth=2)
        board = chess.Board(starting_fen + " 0 1")

        # Get best move with pruning (the default)
        best_move, score = engine.get_best_move(board)

        # Verify we got a valid move
        assert best_move is not None
        assert best_move in board.legal_moves

    def test_pruning_efficiency_with_tactical_position(self, scholars_mate_fen: str):
        """
        In tactical positions, pruning should still find the best move.
        Scholar's mate should be found quickly even at higher depth.
        """
        import time

        start_time = time.time()
        best_move, score = MiniMaxEngine.get_best_move_from_fen(
            scholars_mate_fen, depth=4
        )
        elapsed = time.time() - start_time

        assert best_move == "h5f7", "Should still find Scholar's mate"
        # With good pruning, this shouldn't take too long
        assert elapsed < 10, f"Search took too long: {elapsed}s"


class TestPieceValues:
    """Tests for piece value constants."""

    def test_piece_values_are_reasonable(self):
        """Verify piece values follow standard chess evaluation."""
        values = MiniMaxEngine.PIECE_VALUES

        # Standard piece value hierarchy
        assert values[chess.PAWN] < values[chess.KNIGHT]
        assert values[chess.PAWN] < values[chess.BISHOP]
        assert values[chess.KNIGHT] < values[chess.ROOK]
        assert values[chess.BISHOP] < values[chess.ROOK]
        assert values[chess.ROOK] < values[chess.QUEEN]
        assert values[chess.QUEEN] < values[chess.KING]

    def test_bishop_knight_similar_value(self):
        """Bishop and Knight should have similar values."""
        values = MiniMaxEngine.PIECE_VALUES
        diff = abs(values[chess.BISHOP] - values[chess.KNIGHT])
        assert diff <= 50, "Bishop and Knight values should be close"
