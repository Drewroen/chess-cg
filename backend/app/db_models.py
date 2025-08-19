from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String)
    username = Column(String, unique=True, index=True, nullable=True)
    user_type = Column(
        String, default="authenticated", nullable=False
    )  # "authenticated" or "guest"
    elo = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ChessGame(Base):
    __tablename__ = "chess_games"

    id = Column(String, primary_key=True)
    white_player_id = Column(String, ForeignKey("users.id"), nullable=False)
    black_player_id = Column(String, ForeignKey("users.id"), nullable=False)
    winner = Column(String, nullable=True)  # "white", "black", "draw", "aborted"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expires_at = Column(DateTime, nullable=True)
