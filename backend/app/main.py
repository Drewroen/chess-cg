from app.svc.room import RoomService, RoomManager, ConnectionManager
from app.svc.time_manager import TimeManager
from app.svc.websocket_handler import WebSocketMessageHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import asyncio
import time
import os
import logging
from dotenv import load_dotenv

from .routers import health, auth, websocket, debug, game
from .obj.game import GameStatus, GAME_START_TIMEOUT_SECONDS
from .auth import cleanup_expired_refresh_tokens, cleanup_expired_guest_tokens
from .database import db_manager

load_dotenv()

# Initialize shared services
room_manager = RoomManager(ConnectionManager(), RoomService())
time_manager = TimeManager()
message_handler = WebSocketMessageHandler(room_manager)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Set up shared services in routers
websocket.room_manager = room_manager
websocket.message_handler = message_handler
debug.room_manager = room_manager
game.room_manager = room_manager
auth.limiter = limiter


async def check_game_timers():
    """Background task to check for time expiration in all active games."""
    while True:
        try:
            current_time = time.time()
            for room_id, room in room_manager.room_service.rooms.items():
                if room.game.status == GameStatus.IN_PROGRESS:
                    # Check if current player has run out of time
                    if time_manager.check_timeout(room.game, current_time):
                        # Update game state to mark timeout
                        time_manager.update_player_time(room.game, current_time)
                        logging.info(f"{room.game.turn.capitalize()} player has run out of time in room {room_id}")
                        room.game.end_reason = "time"
                        await room_manager.emit_game_state_to_room(room_id)
                        await room_manager.cleanup_room_with_elo_update(room_id)

                elif room.game.status == GameStatus.NOT_STARTED:
                    # Check for game start timeout
                    elapsed_since_creation = current_time - room.game.created_at
                    elapsed_since_last_move = current_time - room.game.last_move_time

                    should_abort = False
                    if room.game.turn == "white":
                        # White hasn't moved yet, check time since game creation
                        if elapsed_since_creation >= GAME_START_TIMEOUT_SECONDS:
                            logging.info(
                                f"White player timed out in room {room_id} (no first move)"
                            )
                            should_abort = True
                    else:
                        # Black's turn, check time since white's move
                        if elapsed_since_last_move >= GAME_START_TIMEOUT_SECONDS:
                            logging.info(
                                f"Black player timed out in room {room_id} (no response)"
                            )
                            should_abort = True

                    if should_abort:
                        room.game.status = GameStatus.ABORTED
                        room.game.end_reason = "aborted"
                        room.game.completed_at = current_time
                        room.game.winner = "aborted"
                        await room_manager.emit_game_state_to_room(room_id)
                        await room_manager.room_service.cleanup_room(room_id)
                        continue

                    # Check if both players are disconnected
                    white_connected = (
                        len(
                            room_manager.manager.user_id_to_connection_map.get(
                                room.white, []
                            )
                        )
                        > 0
                    )
                    black_connected = (
                        len(
                            room_manager.manager.user_id_to_connection_map.get(
                                room.black, []
                            )
                        )
                        > 0
                    )

                    if not white_connected and not black_connected:
                        room.game.status = GameStatus.ABORTED
                        room.game.end_reason = "aborted"
                        room.game.completed_at = current_time
                        room.game.winner = "aborted"
                        await room_manager.emit_game_state_to_room(room_id)
                        await room_manager.room_service.cleanup_room(room_id)
        except Exception as e:
            logging.error(f"Error in timer check task: {e}")

        await asyncio.sleep(1)  # Check every 1 second


async def cleanup_expired_tokens():
    """Background task to clean up expired tokens"""
    while True:
        try:
            expired_refresh = (
                await cleanup_expired_refresh_tokens()
            )  # existing function
            expired_guest = cleanup_expired_guest_tokens()  # new function
            if expired_refresh > 0 or expired_guest > 0:
                logging.info(
                    f"Cleaned up {expired_refresh} expired refresh tokens and {expired_guest} expired guest tokens"
                )
        except Exception as e:
            logging.error(f"Error in token cleanup task: {e}")

        await asyncio.sleep(3600)  # Run every hour


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        db_manager.initialize(database_url)
        
        # Warm up database connection pool
        try:
            pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
            logging.info(f"Warming database connection pool (pool_size={pool_size})...")
            start_time = time.time()
            await db_manager.warm_pool()
            elapsed = time.time() - start_time
            logging.info(f"Database connection pool warmed up in {elapsed:.2f}s")
        except Exception as e:
            logging.error(f"Failed to warm database connection pool: {e}")
            # Don't let pool warming failure prevent startup
            logging.warning("Continuing startup despite pool warming failure")

    timer_task = asyncio.create_task(check_game_timers())
    cleanup_task = asyncio.create_task(cleanup_expired_tokens())
    yield
    # Shutdown
    timer_task.cancel()
    cleanup_task.cancel()
    await db_manager.close()


app = FastAPI(
    title="Chess CG API",
    description="A chess game backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state for global access
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://rechess.club"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(websocket.router)
app.include_router(debug.router)
app.include_router(game.router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
