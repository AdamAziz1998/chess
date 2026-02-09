from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import models
import schemas
import crud
import database
from minimax.minimax import MiniMaxEngine
from engine import best_move

# Create tables on startup (For dev only - use Alembic for Prod)
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/engine")
@limiter.limit("45 per minute")
async def engine(request: Request, fen: str) -> str:
    """
    Input a fen position, returns the best calculated move
    """
    return await best_move(fen)



@app.post("/moves/", response_model=schemas.MoveResponse)
@limiter.limit("10 per minute")
async def add_move(
    request: Request,
    move_data: schemas.MoveCreate,
    db: AsyncSession = Depends(database.get_db),
):
    """
    Upload a move. automatically creates the Start/End Positions
    if they don't exist yet.
    """
    return await crud.create_move_record(db, move_data)


@app.get("/position/", response_model=schemas.PositionWithMoves)
@limiter.limit("10 per minute")
async def get_position(
    request: Request, fen: str, db: AsyncSession = Depends(database.get_db)
):
    """
    Get a position and all available moves from it.
    """
    position = await crud.get_position_with_moves(db, fen)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position


# Helper to calculate total games directly in Python
def calculate_total(m: models.Move):
    return m.white + m.black + m.draw


@app.get("/stats", response_model=schemas.PositionStatsResponse)
@limiter.limit("30 per minute")
async def get_stats_by_fen(
    request: Request, fen: str, db: AsyncSession = Depends(database.get_db)
):
    """
    Search for a given FEN and return stats for all moves from that position.
    """
    # 1. Find the Position
    stmt = (
        select(models.Position)
        .options(
            selectinload(models.Position.moves_from)
        )  # This fetches the moves immediately
        .where(models.Position.fen_position == fen)
    )
    result = await db.execute(stmt)
    position = result.scalars().first()

    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    # 2. Format response
    # Because we used lazy="selectin" in models.py, accessing .moves is async-safe
    move_stats = []
    for move in position.moves_from:
        move_stats.append(
            {
                "move": move.move,
                "white": move.white,
                "black": move.black,
                "draw": move.draw,
                "total_games": move.white + move.black + move.draw,
            }
        )

    # Sort by popularity (optional, but helpful)
    move_stats.sort(key=lambda x: x["total_games"], reverse=True)

    return {"fen": position.fen_position, "moves": move_stats}


@app.get("/historical", response_model=schemas.MoveStat)
@limiter.limit("50 per minute")
async def get_popular_move(
    request: Request, fen: str, db: AsyncSession = Depends(database.get_db)
):
    """
    Return ONLY the most historically popular move from this position.
    """
    # 1. Get Position ID first
    pos_stmt = select(models.Position.id).where(models.Position.fen_position == fen)
    pos_result = await db.execute(pos_stmt)
    pos_id = pos_result.scalars().first()

    if not pos_id:
        raise HTTPException(status_code=404, detail="Position not found")

    # 2. Query Move table directly, sorting by sum of columns
    # Formula: (white + black + draw)
    total_games_expr = models.Move.white + models.Move.black + models.Move.draw

    move_stmt = (
        select(models.Move)
        .where(models.Move.fen_id == pos_id)
        .order_by(desc(total_games_expr))
        .limit(1)
    )

    move_result = await db.execute(move_stmt)
    best_move = move_result.scalars().first()

    if not best_move:
        raise HTTPException(
            status_code=404, detail="No moves recorded for this position"
        )

    return {
        "move": best_move.move,
        "white": best_move.white,
        "black": best_move.black,
        "draw": best_move.draw,
        "total_games": best_move.white + best_move.black + best_move.draw,
    }


@app.get("/minimax")
@limiter.limit("10 per minute")
def calculate_minimax(request: Request, fen: str, depth: int = 4):
    """
    Calculates the best move using the MiniMax engine.
    Note: This runs synchronously in a thread pool to avoid blocking async DB operations.
    """
    # 1. Use the static method from your MiniMaxEngine class
    best_move_uci, score = MiniMaxEngine.get_best_move_from_fen(fen, depth=depth)

    # 2. Handle invalid FEN
    if best_move_uci is None and score == 0:
        raise HTTPException(status_code=400, detail="Invalid FEN string")

    # 3. Determine status based on the engine's return logic
    status = "active"
    if best_move_uci is None:
        # If no move, check the score to see result
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
