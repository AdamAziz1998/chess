from pydantic import BaseModel


class MoveStat(BaseModel):
    move: str
    white: int
    black: int
    draw: int
    total_games: int


class PositionStatsResponse(BaseModel):
    fen: str
    moves: list[MoveStat]
