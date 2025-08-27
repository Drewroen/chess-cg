from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    def initialize(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,          # Number of persistent connections
            max_overflow=20,       # Additional connections beyond pool_size
            pool_timeout=30,       # Timeout when getting connection from pool
            pool_recycle=3600,     # Recycle connections after 1 hour
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


