from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from urllib.parse import unquote

import schemas
import os
from minimax.minimax import MiniMaxEngine

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from engine import best_move
from lichess import get_lichess_stats, get_most_popular_move


TESTING = os.getenv("TESTING", "False").lower() == "true"
limiter = Limiter(key_func=get_remote_address, enabled=not TESTING)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/engine/{fen:path}")
@limiter.limit("45 per minute")
async def engine(request: Request, fen: str) -> str:
    """
    Input a fen position as a path, returns the best calculated move.
    Checks the Lichess opening explorer first, then falls back to minimax/neural network.
    """
    cleaned_fen = unquote(fen)
    return await best_move(cleaned_fen)


@app.get("/stats/{fen:path}", response_model=schemas.PositionStatsResponse)
@limiter.limit("30 per minute")
async def get_stats_by_fen(request: Request, fen: str):
    """
    Returns move statistics for a position from the Lichess opening explorer.
    """
    cleaned_fen = unquote(fen)
    data = await get_lichess_stats(cleaned_fen)

    if not data:
        raise HTTPException(status_code=404, detail="Position not found")

    move_stats = []
    for move in data["moves"]:
        total = move["white"] + move["draws"] + move["black"]
        move_stats.append({
            "move": move["uci"],
            "white": move["white"],
            "black": move["black"],
            "draw": move["draws"],
            "total_games": total,
        })

    move_stats.sort(key=lambda x: x["total_games"], reverse=True)
    return {"fen": cleaned_fen, "moves": move_stats}


@app.get("/historical/{fen:path}", response_model=schemas.MoveStat)
@limiter.limit("50 per minute")
async def get_popular_move(request: Request, fen: str):
    """
    Returns the most popular move for a position from the Lichess opening explorer.
    """
    cleaned_fen = unquote(fen)
    move = await get_most_popular_move(cleaned_fen)

    if not move:
        raise HTTPException(status_code=404, detail="Position not found")

    return move


@app.get("/minimax/{fen:path}")
@limiter.limit("10 per minute")
def calculate_minimax(request: Request, fen: str, depth: int = 4):
    cleaned_fen = unquote(fen)

    best_move_uci, score = MiniMaxEngine.get_best_move_from_fen(cleaned_fen, depth=depth)

    if best_move_uci is None and score == 0:
        raise HTTPException(status_code=400, detail="Invalid FEN string")

    status = "active"
    if best_move_uci is None:
        if abs(score) == MiniMaxEngine.MATE_SCORE:
            status = "checkmate"
        elif score == 0:
            status = "stalemate"

    return {
        "best_move": best_move_uci,
        "score": score,
        "depth": depth,
        "status": status,
    }
