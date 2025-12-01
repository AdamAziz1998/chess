from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base
from typing import List

class Position(Base):
    __tablename__ = "position"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fen_position: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationships
    # Moves played FROM this position
    moves_from: Mapped[List["Move"]] = relationship(
        "Move", 
        foreign_keys="[Move.fen_id]", 
        back_populates="start_pos"
    )
    
    # Moves resulting IN this position (optional, but good for graph traversal)
    moves_to: Mapped[List["Move"]] = relationship(
        "Move", 
        foreign_keys="[Move.new_fen_id]", 
        back_populates="end_pos"
    )

class Move(Base):
    __tablename__ = "move"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys
    fen_id: Mapped[int] = mapped_column(ForeignKey("position.id", ondelete="CASCADE"))
    new_fen_id: Mapped[int] = mapped_column(ForeignKey("position.id", ondelete="CASCADE"))
    
    move: Mapped[str] = mapped_column(String, nullable=False)
    
    # Stats
    white: Mapped[int] = mapped_column(Integer, default=0)
    black: Mapped[int] = mapped_column(Integer, default=0)
    draw: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships linking back to Position
    start_pos: Mapped["Position"] = relationship(
        "Position", 
        foreign_keys=[fen_id], 
        back_populates="moves_from"
    )
    
    end_pos: Mapped["Position"] = relationship(
        "Position", 
        foreign_keys=[new_fen_id], 
        back_populates="moves_to"
    )

    __table_args__ = (
        UniqueConstraint('fen_id', 'new_fen_id', name='uix_move_fen_new_fen'),
    )