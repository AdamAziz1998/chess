"""
Shared pytest fixtures for Chess backend tests.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from ..database import Base, get_db
from ..main import app


# Use in-memory SQLite for fast, isolated tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db():
    """
    Create a fresh in-memory SQLite database for each test.
    Yields an AsyncSession and cleans up afterward.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Required for SQLite in-memory to share connection
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession):
    """
    Provide an async test client with the database dependency overridden.
    """

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


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
