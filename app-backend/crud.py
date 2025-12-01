from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from . import models, schemas

async def get_position_by_fen(db: AsyncSession, fen: str):
    result = await db.execute(select(models.Position).where(models.Position.fen_position == fen))
    return result.scalars().first()

async def create_position(db: AsyncSession, fen: str):
    # Check if exists first
    existing = await get_position_by_fen(db, fen)
    if existing:
        return existing
    
    new_pos = models.Position(fen_position=fen)
    db.add(new_pos)
    await db.commit()
    await db.refresh(new_pos)
    return new_pos

async def get_position_with_moves(db: AsyncSession, fen: str):
    # Eager load the moves to prevent N+1 queries
    stmt = (
        select(models.Position)
        .where(models.Position.fen_position == fen)
        .options(select.inload(models.Position.moves_from))
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_move_record(db: AsyncSession, move_data: schemas.MoveCreate):
    # 1. Ensure Start Position exists
    start_pos = await create_position(db, move_data.start_fen)
    
    # 2. Ensure End Position exists
    end_pos = await create_position(db, move_data.end_fen)

    # 3. Check if this specific move link already exists
    stmt = select(models.Move).where(
        models.Move.fen_id == start_pos.id,
        models.Move.new_fen_id == end_pos.id
    )
    result = await db.execute(stmt)
    existing_move = result.scalars().first()

    if existing_move:
        # Optional: Logic to update stats if move exists?
        # For now, just return existing
        return existing_move

    # 4. Create new Move
    new_move = models.Move(
        fen_id=start_pos.id,
        new_fen_id=end_pos.id,
        move=move_data.move,
        white=move_data.white,
        black=move_data.black,
        draw=move_data.draw
    )
    db.add(new_move)
    await db.commit()
    await db.refresh(new_move)
    return new_move