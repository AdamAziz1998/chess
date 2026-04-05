from pydantic import BaseModel
from typing import Optional, Any

class MoveStat(BaseModel):
    move: str
    white: int
    black: int
    draw: int
    total_games: int

class PositionStatsResponse(BaseModel):
    fen: str
    moves: list[MoveStat]

class Player(BaseModel):
    name: str
    rating: int

class Game(BaseModel):
    uci: str
    id: str
    winner: Optional[str] = None
    speed: str
    mode: str
    black: Player
    white: Player
    year: int
    month: str

class Opening(BaseModel):
    eco: str
    name: str

class HistoricalMoveData(BaseModel):
    uci: str
    san: str
    averageRating: int
    white: int
    draws: int
    black: int
    game: Optional[Any] = None
    opening: Optional[Opening] = None

class HistoricalData(BaseModel):
    white: int
    draws: int
    black: int
    moves: list[HistoricalMoveData]
    recentGames: list[Game]
    topGames: list[Game]
    opening: Optional[Opening] = None
