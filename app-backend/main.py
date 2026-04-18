import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from urllib.parse import unquote

import schemas
import os
from dotenv import load_dotenv

load_dotenv()

from minimax.minimax import MiniMaxEngine
from engine import best_move
from lichess import get_lichess_stats


TESTING = os.getenv("TESTING", "False").lower() == "true"
limiter = Limiter(key_func=get_remote_address, enabled=not TESTING)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),

    traces_sample_rate=0.05,
    profiles_sample_rate=0.05,

    send_default_pii=True,
)

app = FastAPI()

# Fallback to localhost for dev, use comma-separated list in production.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS", "POST"],
    allow_headers=["Accept", "Content-Type", "Origin"],
)

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


@app.get("/historical/{fen:path}", response_model=schemas.HistoricalData)
@limiter.limit("50 per minute")
async def get_historical_data(request: Request, fen: str):
    """
    Returns the full historical data for a position from the Lichess opening explorer.
    """
    cleaned_fen = unquote(fen)
    move_data = await get_lichess_stats(cleaned_fen)

    if not move_data:
        raise HTTPException(status_code=404, detail="Position not found")

    return move_data


@app.get("/minimax/{fen:path}")
@limiter.limit("10 per minute")
def calculate_minimax(request: Request, fen: str, depth: int = 4):
    cleaned_fen = unquote(fen)

    try:
        best_move_uci, score = MiniMaxEngine.get_best_move_from_fen(cleaned_fen, depth=depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI Engine failed to evaluate position")

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
