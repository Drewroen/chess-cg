from sqlalchemy import Column, String, DateTime, Integer, Index
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
