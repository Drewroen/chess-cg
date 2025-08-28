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

    async def warm_pool(self):
        """Pre-warm database connection pool by creating and testing connections"""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")

        # Create test connections to warm the pool
        pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        # Warm up to 75% of pool size, minimum 3, maximum 15 connections
        warm_count = max(3, min(15, int(pool_size * 0.75)))
        connections = []

        try:
            # Acquire connections up to warm_count to warm them up
            for i in range(warm_count):
                conn = await self.engine.connect()
                # Execute a simple query to ensure connection is working
                await conn.execute("SELECT 1")
                connections.append(conn)

            # Return connections to pool
            for conn in connections:
                await conn.close()

        except Exception as e:
            # Clean up any connections we managed to create
            for conn in connections:
                try:
                    await conn.close()
                except Exception:
                    pass
            raise e

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
