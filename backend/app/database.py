from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    def initialize(self, database_url: str):
        # Environment-configurable pool settings for chess game load optimization
        pool_size = int(
            os.getenv("DB_POOL_SIZE", "20")
        )  # Increased for concurrent games
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "30"))  # Increased overflow
        pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour

        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self):
        if self.engine:
            await self.engine.dispose()


db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
