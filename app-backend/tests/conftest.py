"""
Shared pytest fixtures for Chess backend tests.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Set TESTING env var BEFORE importing app so the limiter is disabled at import time
os.environ["TESTING"] = "True"

from main import app


@pytest_asyncio.fixture
async def client():
    """
    Provide an async test client for the FastAPI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# Common FEN strings for testing
@pytest.fixture
def starting_fen() -> str:
    """Standard chess starting position."""
    return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"


@pytest.fixture
def scholars_mate_fen() -> str:
    """Position where White can deliver Scholar's Mate (Qxf7#)."""
    return "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq -"


@pytest.fixture
def endgame_kq_vs_k_fen() -> str:
    """King + Queen vs King endgame - White to force checkmate."""
    return "8/8/8/4k3/8/8/3QK3/8 w - -"


@pytest.fixture
def black_checkmate_fen() -> str:
    """Black is checkmated (back rank mate)."""
    return "6k1/5ppp/8/8/8/8/8/R3K3 b - -"


@pytest.fixture
def stalemate_fen() -> str:
    """Stalemate position - Black to move, no legal moves, not in check."""
    return "k7/8/1K6/8/8/8/8/8 b - -"


@pytest.fixture
def after_e4_fen() -> str:
    """Position after 1. e4"""
    return "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"
