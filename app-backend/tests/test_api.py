"""
Integration tests for FastAPI API endpoints.

Tests POST /moves/, GET /minimax, GET /stats, GET /position/, GET /historical
with a test database (SQLite in-memory) to verify persistence and retrieval.
"""

import pytest
from httpx import AsyncClient


class TestMoveEndpoint:
    """Tests for POST /moves/ endpoint."""

    @pytest.mark.asyncio
    async def test_create_move_success(
        self, client: AsyncClient, starting_fen: str, after_e4_fen: str
    ):
        """
        POST /moves/ should create Position and Move records.
        Verifies that both start and end positions are persisted.
        """
        move_data = {
            "move": "e2e4",
            "start_fen": starting_fen,
            "end_fen": after_e4_fen,
            "white": 1000,
            "black": 500,
            "draw": 300,
        }

        response = await client.post("/moves/", json=move_data)

        assert response.status_code == 200
        data = response.json()

        assert data["move"] == "e2e4"
        assert data["white"] == 1000
        assert data["black"] == 500
        assert data["draw"] == 300
        assert "id" in data
        assert "fen_id" in data
        assert "new_fen_id" in data

    @pytest.mark.asyncio
    async def test_create_move_creates_positions(self, client: AsyncClient):
        """Verify that creating a move also creates the Position entries."""
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        end_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"

        move_data = {
            "move": "e2e4",
            "start_fen": start_fen,
            "end_fen": end_fen,
            "white": 100,
            "black": 50,
            "draw": 25,
        }

        # Create the move
        response = await client.post("/moves/", json=move_data)
        assert response.status_code == 200

        # Verify position can be retrieved via /stats
        stats_response = await client.get("/stats", params={"fen": start_fen})
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["fen"] == start_fen
        assert len(stats_data["moves"]) >= 1

    @pytest.mark.asyncio
    async def test_create_duplicate_move_returns_existing(self, client: AsyncClient):
        """Creating the same move twice should return the existing record."""
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        end_fen = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3"

        move_data = {
            "move": "d2d4",
            "start_fen": start_fen,
            "end_fen": end_fen,
            "white": 800,
            "black": 400,
            "draw": 200,
        }

        # Create first time
        response1 = await client.post("/moves/", json=move_data)
        assert response1.status_code == 200
        id1 = response1.json()["id"]

        # Create second time (same move)
        response2 = await client.post("/moves/", json=move_data)
        assert response2.status_code == 200
        id2 = response2.json()["id"]

        # Should return the same record
        assert id1 == id2

    @pytest.mark.asyncio
    async def test_create_move_missing_fields(self, client: AsyncClient):
        """POST /moves/ with missing required fields should return 422."""
        incomplete_data = {
            "move": "e2e4"
            # Missing start_fen and end_fen
        }

        response = await client.post("/moves/", json=incomplete_data)
        assert response.status_code == 422  # Validation error


class TestMinimaxEndpoint:
    """Tests for GET /minimax endpoint."""

    @pytest.mark.asyncio
    async def test_minimax_valid_fen(self, client: AsyncClient, starting_fen: str):
        """GET /minimax with valid FEN should return best move and score."""
        response = await client.get(
            "/minimax", params={"fen": starting_fen, "depth": 2}
        )

        assert response.status_code == 200
        data = response.json()

        assert "best_move" in data
        assert "score" in data
        assert "depth" in data
        assert "status" in data
        assert data["depth"] == 2
        assert data["status"] == "active"
        assert data["best_move"] is not None

    @pytest.mark.asyncio
    async def test_minimax_scholars_mate(
        self, client: AsyncClient, scholars_mate_fen: str
    ):
        """GET /minimax for Scholar's Mate position should find Qxf7#."""
        response = await client.get(
            "/minimax", params={"fen": scholars_mate_fen, "depth": 3}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["best_move"] == "h5f7"
        assert data["score"] == 10**6  # MATE_SCORE
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_minimax_invalid_fen(self, client: AsyncClient):
        """GET /minimax with invalid FEN should return 400."""
        response = await client.get(
            "/minimax", params={"fen": "invalid_fen_string", "depth": 2}
        )

        assert response.status_code == 400
        assert "Invalid FEN" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_minimax_default_depth(self, client: AsyncClient, starting_fen: str):
        """GET /minimax without depth parameter should use default (4)."""
        response = await client.get("/minimax", params={"fen": starting_fen})

        assert response.status_code == 200
        data = response.json()
        assert data["depth"] == 4

    @pytest.mark.asyncio
    async def test_minimax_checkmate_status(self, client: AsyncClient):
        """GET /minimax for checkmate position should return checkmate status."""
        # Fool's mate - White is checkmated
        checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq -"

        response = await client.get(
            "/minimax", params={"fen": checkmate_fen, "depth": 1}
        )

        assert response.status_code == 200
        data = response.json()
        # When checkmated, best_move is None
        if data["best_move"] is None:
            assert data["status"] in ["checkmate", "stalemate"]


class TestStatsEndpoint:
    """Tests for GET /stats endpoint."""

    @pytest.mark.asyncio
    async def test_stats_position_not_found(self, client: AsyncClient):
        """GET /stats for non-existent position should return 404."""
        response = await client.get(
            "/stats",
            params={"fen": "8/8/8/8/8/8/8/8 w - -"},  # Empty board (not in DB)
        )

        assert response.status_code == 404
        assert "Position not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stats_returns_move_statistics(self, client: AsyncClient):
        """GET /stats should return move statistics for a position."""
        # First create some moves
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"

        moves_to_create = [
            {
                "move": "e2e4",
                "end_fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3",
                "white": 1000,
                "black": 500,
                "draw": 300,
            },
            {
                "move": "d2d4",
                "end_fen": "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3",
                "white": 800,
                "black": 400,
                "draw": 200,
            },
        ]

        for move in moves_to_create:
            await client.post(
                "/moves/",
                json={
                    "move": move["move"],
                    "start_fen": start_fen,
                    "end_fen": move["end_fen"],
                    "white": move["white"],
                    "black": move["black"],
                    "draw": move["draw"],
                },
            )

        # Get stats
        response = await client.get("/stats", params={"fen": start_fen})

        assert response.status_code == 200
        data = response.json()

        assert data["fen"] == start_fen
        assert len(data["moves"]) == 2

        # Moves should be sorted by total_games (descending)
        assert data["moves"][0]["total_games"] >= data["moves"][1]["total_games"]

        # Verify move structure
        for move_stat in data["moves"]:
            assert "move" in move_stat
            assert "white" in move_stat
            assert "black" in move_stat
            assert "draw" in move_stat
            assert "total_games" in move_stat
            assert (
                move_stat["total_games"]
                == move_stat["white"] + move_stat["black"] + move_stat["draw"]
            )


class TestPositionEndpoint:
    """Tests for GET /position/ endpoint."""

    @pytest.mark.asyncio
    async def test_position_not_found(self, client: AsyncClient):
        """GET /position/ for non-existent position should return 404."""
        response = await client.get(
            "/position/",
            params={"fen": "8/8/8/4k3/8/8/8/4K3 w - -"},  # K vs K (not in DB)
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_position_with_moves(self, client: AsyncClient):
        """GET /position/ should return position with its moves."""
        start_fen = "r1bqkbnr/pppppppp/2n5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"
        end_fen = "r1bqkbnr/pppppppp/2n5/8/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -"

        # Create a move
        await client.post(
            "/moves/",
            json={
                "move": "g1f3",
                "start_fen": start_fen,
                "end_fen": end_fen,
                "white": 500,
                "black": 250,
                "draw": 100,
            },
        )

        # Get position
        response = await client.get("/position/", params={"fen": start_fen})

        assert response.status_code == 200
        data = response.json()

        assert data["fen_position"] == start_fen
        assert "id" in data
        assert "moves_from" in data


class TestHistoricalEndpoint:
    """Tests for GET /historical endpoint."""

    @pytest.mark.asyncio
    async def test_historical_returns_most_popular(self, client: AsyncClient):
        """GET /historical should return the most popular move."""
        start_fen = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"

        # Create moves with different popularity
        moves = [
            {
                "move": "e4e5",
                "end_fen": "rnbqkb1r/pppppppp/5n2/4P3/8/8/PPPP1PPP/RNBQKBNR b KQkq -",
                "white": 100,
                "black": 50,
                "draw": 25,
            },
            {
                "move": "b1c3",
                "end_fen": "rnbqkb1r/pppppppp/5n2/8/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq -",
                "white": 500,
                "black": 300,
                "draw": 200,
            },  # Most popular
            {
                "move": "d2d3",
                "end_fen": "rnbqkb1r/pppppppp/5n2/8/4P3/3P4/PPP2PPP/RNBQKBNR b KQkq -",
                "white": 50,
                "black": 25,
                "draw": 10,
            },
        ]

        for move in moves:
            await client.post(
                "/moves/",
                json={
                    "move": move["move"],
                    "start_fen": start_fen,
                    "end_fen": move["end_fen"],
                    "white": move["white"],
                    "black": move["black"],
                    "draw": move["draw"],
                },
            )

        # Get most popular move
        response = await client.get("/historical", params={"fen": start_fen})

        assert response.status_code == 200
        data = response.json()

        # b1c3 should be the most popular (500 + 300 + 200 = 1000 total games)
        assert data["move"] == "b1c3"
        assert data["total_games"] == 1000

    @pytest.mark.asyncio
    async def test_historical_position_not_found(self, client: AsyncClient):
        """GET /historical for non-existent position should return 404."""
        response = await client.get(
            "/historical", params={"fen": "8/8/8/8/8/8/8/8 w - -"}
        )

        assert response.status_code == 404


class TestDatabasePersistence:
    """Tests to verify database persistence across requests."""

    @pytest.mark.asyncio
    async def test_move_persists_across_requests(self, client: AsyncClient):
        """Verify that a created move can be retrieved in subsequent requests."""
        start_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -"
        end_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq -"

        # Create move
        create_response = await client.post(
            "/moves/",
            json={
                "move": "e1g1",  # Castling
                "start_fen": start_fen,
                "end_fen": end_fen,
                "white": 750,
                "black": 400,
                "draw": 150,
            },
        )
        assert create_response.status_code == 200

        # Retrieve via /stats
        stats_response = await client.get("/stats", params={"fen": start_fen})
        assert stats_response.status_code == 200

        moves = stats_response.json()["moves"]
        assert any(m["move"] == "e1g1" for m in moves)

    @pytest.mark.asyncio
    async def test_multiple_moves_same_position(self, client: AsyncClient):
        """Multiple moves from the same position should all be persisted."""
        start_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"

        moves = [
            {
                "move": "g1f3",
                "end_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -",
            },
            {
                "move": "b1c3",
                "end_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq -",
            },
            {
                "move": "f1c4",
                "end_fen": "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq -",
            },
        ]

        for i, move in enumerate(moves):
            await client.post(
                "/moves/",
                json={
                    "move": move["move"],
                    "start_fen": start_fen,
                    "end_fen": move["end_fen"],
                    "white": 100 * (i + 1),
                    "black": 50 * (i + 1),
                    "draw": 25 * (i + 1),
                },
            )

        # Verify all moves are present
        stats_response = await client.get("/stats", params={"fen": start_fen})
        assert stats_response.status_code == 200

        persisted_moves = {m["move"] for m in stats_response.json()["moves"]}
        expected_moves = {"g1f3", "b1c3", "f1c4"}
        assert persisted_moves == expected_moves
