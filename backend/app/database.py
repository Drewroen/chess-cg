from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import DisconnectionError, OperationalError
from typing import AsyncGenerator
import asyncio
import logging


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
            pool_pre_ping=True,  # Verify connections before use
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
        )

    async def close(self):
        if self.engine:
            await self.engine.dispose()


db_manager = DatabaseManager()


async def get_db_session(max_retries: int = 3) -> AsyncGenerator[AsyncSession, None]:
    """Get database session with connection retry logic"""
    for attempt in range(max_retries):
        try:
            async with db_manager.async_session_maker() as session:
                yield session
                return
        except (DisconnectionError, OperationalError) as e:
            if attempt == max_retries - 1:
                logging.error(
                    f"Database connection failed after {max_retries} attempts: {e}"
                )
                raise
            logging.warning(
                f"Database connection attempt {attempt + 1} failed, retrying: {e}"
            )
            await asyncio.sleep(0.1 * (2**attempt))  # Exponential backoff
        except Exception as e:
            logging.error(f"Unexpected database error: {e}")
            raise
