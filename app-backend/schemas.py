from pydantic import BaseModel
from typing import List

# --- Position Schemas ---
class PositionBase(BaseModel):
    fen_position: str

class PositionCreate(PositionBase):
    pass

class PositionResponse(PositionBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Move Schemas ---
class MoveBase(BaseModel):
    move: str
    white: int = 0
    black: int = 0
    draw: int = 0

class MoveCreate(MoveBase):
    # We allow creating a move by providing the FEN strings directly
    # This is much easier for the client than knowing IDs beforehand
    start_fen: str
    end_fen: str 

class MoveResponse(MoveBase):
    id: int
    fen_id: int
    new_fen_id: int
    
    class Config:
        from_attributes = True

# Extended schema to see moves inside a position response
class PositionWithMoves(PositionResponse):
    moves_from: List[MoveResponse] = []

class MoveStat(BaseModel):
    move: str
    white: int
    black: int
    draw: int
    total_games: int

class PositionStatsResponse(BaseModel):
    fen: str
    moves: list[MoveStat]