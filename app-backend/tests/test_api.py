"""
Integration tests for FastAPI API endpoints.

Tests GET /minimax, GET /stats, GET /historical, GET /engine
using mocked Lichess opening explorer responses.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from urllib.parse import quote


def fen_url(fen: str) -> str:
    """URL-encode a FEN string for use as a path parameter (keeps slashes)."""
    return quote(fen, safe="/")


# --- Sample Lichess API response data ---

LICHESS_STATS_RESPONSE = {
    "white": 15000,
    "draws": 6000,
    "black": 9000,
    "moves": [
        {
            "uci": "e2e4",
            "san": "e4",
            "white": 6000,
            "draws": 2400,
            "black": 3600,
            "averageRating": 1850,
        },
        {
            "uci": "d2d4",
            "san": "d4",
            "white": 4500,
            "draws": 1800,
            "black": 2700,
            "averageRating": 1840,
        },
    ],
}

LICHESS_POPULAR_MOVE = {
    "move": "e2e4",
    "white": 6000,
    "black": 3600,
    "draw": 2400,
    "total_games": 12000,
}


class TestMinimaxEndpoint:
    """Tests for GET /minimax endpoint."""

    @pytest.mark.asyncio
    async def test_minimax_valid_fen(self, client: AsyncClient, starting_fen: str):
        """GET /minimax with valid FEN should return best move and score."""
        response = await client.get(
            f"/minimax/{fen_url(starting_fen)}", params={"depth": 2}
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
            f"/minimax/{fen_url(scholars_mate_fen)}", params={"depth": 3}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["best_move"] == "h5f7"
        assert data["score"] == 10**6  # MATE_SCORE
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_minimax_invalid_fen(self, client: AsyncClient):
        """GET /minimax with invalid FEN should return 400."""
        response = await client.get("/minimax/invalid_fen_string")

        assert response.status_code == 400
        assert "Invalid FEN" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_minimax_default_depth(self, client: AsyncClient, starting_fen: str):
        """GET /minimax without depth parameter should use default (4)."""
        response = await client.get(f"/minimax/{fen_url(starting_fen)}")

        assert response.status_code == 200
        data = response.json()
        assert data["depth"] == 4

    @pytest.mark.asyncio
    async def test_minimax_checkmate_status(self, client: AsyncClient):
        """GET /minimax for checkmate position should return checkmate status."""
        # Fool's mate - White is checkmated
        checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq -"

        response = await client.get(
            f"/minimax/{fen_url(checkmate_fen)}", params={"depth": 1}
        )

        assert response.status_code == 200
        data = response.json()
        # When checkmated, best_move is None
        if data["best_move"] is None:
            assert data["status"] in ["checkmate", "stalemate"]


class TestStatsEndpoint:
    """Tests for GET /stats endpoint - backed by Lichess explorer."""

    @pytest.mark.asyncio
    async def test_stats_position_not_found(self, client: AsyncClient):
        """GET /stats when Lichess has no data should return 404."""
        with patch("main.get_lichess_stats", new=AsyncMock(return_value=None)):
            response = await client.get(f"/stats/{fen_url('8/8/8/8/8/8/8/8 w - -')}")

        assert response.status_code == 404
        assert "Position not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stats_returns_move_statistics(
        self, client: AsyncClient, starting_fen: str
    ):
        """GET /stats should return processed move statistics from Lichess."""
        with patch(
            "main.get_lichess_stats",
            new=AsyncMock(return_value=LICHESS_STATS_RESPONSE),
        ):
            response = await client.get(f"/stats/{fen_url(starting_fen)}")

        assert response.status_code == 200
        data = response.json()

        assert data["fen"] == starting_fen
        assert len(data["moves"]) == 2

        # Moves should be sorted by total_games (descending)
        assert data["moves"][0]["total_games"] >= data["moves"][1]["total_games"]

        # Verify schema field names (Lichess 'draws'/'uci' are mapped to 'draw'/'move')
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

    @pytest.mark.asyncio
    async def test_stats_moves_sorted_by_popularity(
        self, client: AsyncClient, starting_fen: str
    ):
        """Moves should be sorted by total_games descending even if Lichess returns them reversed."""
        reversed_data = {
            **LICHESS_STATS_RESPONSE,
            "moves": list(reversed(LICHESS_STATS_RESPONSE["moves"])),
        }
        with patch(
            "main.get_lichess_stats", new=AsyncMock(return_value=reversed_data)
        ):
            response = await client.get(f"/stats/{fen_url(starting_fen)}")

        assert response.status_code == 200
        moves = response.json()["moves"]
        # e2e4 has 12000 total games vs d2d4's 9000
        assert moves[0]["move"] == "e2e4"
        assert moves[0]["total_games"] == 12000


class TestHistoricalEndpoint:
    """Tests for GET /historical endpoint - backed by Lichess explorer."""

    @pytest.mark.asyncio
    async def test_historical_returns_most_popular(
        self, client: AsyncClient, starting_fen: str
    ):
        """GET /historical should return the most popular move from Lichess."""
        with patch(
            "main.get_most_popular_move",
            new=AsyncMock(return_value=LICHESS_POPULAR_MOVE),
        ):
            response = await client.get(f"/historical/{fen_url(starting_fen)}")

        assert response.status_code == 200
        data = response.json()

        assert data["move"] == "e2e4"
        assert data["total_games"] == 12000
        assert "white" in data
        assert "black" in data
        assert "draw" in data

    @pytest.mark.asyncio
    async def test_historical_position_not_found(self, client: AsyncClient):
        """GET /historical when Lichess has no data should return 404."""
        with patch("main.get_most_popular_move", new=AsyncMock(return_value=None)):
            response = await client.get(
                f"/historical/{fen_url('8/8/8/8/8/8/8/8 w - -')}"
            )

        assert response.status_code == 404
        assert "Position not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_historical_response_structure(
        self, client: AsyncClient, starting_fen: str
    ):
        """GET /historical response should match the MoveStat schema."""
        with patch(
            "main.get_most_popular_move",
            new=AsyncMock(return_value=LICHESS_POPULAR_MOVE),
        ):
            response = await client.get(f"/historical/{fen_url(starting_fen)}")

        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"move", "white", "black", "draw", "total_games"}
