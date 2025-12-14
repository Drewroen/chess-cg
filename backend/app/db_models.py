from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

if TYPE_CHECKING:
    from app.routers.game import Loadout


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String)
    username: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    user_type: Mapped[str] = mapped_column(
        String, default="authenticated", nullable=False
    )  # "authenticated" or "guest"
    elo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    loadout: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # Stores piece modifiers loadout as JSON - structure matches Loadout model
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def get_loadout_model(self) -> Optional["Loadout"]:
        """Convert loadout dict to Loadout model"""
        if not self.loadout:
            return None
        from app.routers.game import Loadout

        return Loadout(**self.loadout)


class ChessGame(Base):
    __tablename__ = "chess_games"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    white_player_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    black_player_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    winner: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # "white", "black", "draw", "aborted"
    end_reason: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # "checkmate", "stalemate", "time", "resignation", "draw_agreement", "aborted"
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    google_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    google_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
