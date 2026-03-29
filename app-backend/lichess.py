"""
Client for the Lichess opening explorer API.
https://explorer.lichess.ovh
"""
import os
import httpx
import logging
from typing import Optional
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

LICHESS_EXPLORER_URL = "https://explorer.lichess.ovh"


def _auth_headers() -> dict:
    """Build Authorization headers from the LICHESS_API_TOKEN env var."""
    token = os.getenv("LICHESS_API_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def query_explorer(fen: str, source: str = "lichess") -> Optional[dict]:
    """Query the Lichess opening explorer API for a given FEN position.

    Returns the raw response dict if moves exist, otherwise None.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LICHESS_EXPLORER_URL}/{source}",
                params={"fen": fen},
                headers=_auth_headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data if data.get("moves") else None
    except Exception:
        return None


import chess

def _standardize_uci(uci: str, fen: str) -> str:
    try:
        return chess.Board(fen).parse_uci(uci).uci()
    except Exception:
        return uci

async def get_lichess_stats(fen: str) -> Optional[dict]:
    """Get move statistics for a position from the Lichess explorer.

    Returns the raw Lichess response (moves use 'uci' and 'draws' keys).
    """
    data = await query_explorer(fen)
    if data and "moves" in data:
        for m in data["moves"]:
            m["uci"] = _standardize_uci(m["uci"], fen)
    return data

async def get_most_popular_move(fen: str) -> Optional[dict]:
    """Get the most popular move for a position from the Lichess explorer.

    Returns a dict with keys: move, white, black, draw, total_games, or None.
    """
    data = await query_explorer(fen)
    logger.info("Move 1: %s", data)
    if not data:
        return None
    top_move = data["moves"][0]
    return {
        "move": _standardize_uci(top_move["uci"], fen),
        "white": top_move["white"],
        "black": top_move["black"],
        "draw": top_move["draws"],
        "total_games": top_move["white"] + top_move["draws"] + top_move["black"],
    }
