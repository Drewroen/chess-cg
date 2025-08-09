from app.svc.room import RoomService, RoomManager, ConnectionManager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import time

from .routers import health, auth, websocket, debug
from .obj.game import GameStatus
from .auth import cleanup_expired_refresh_tokens, cleanup_expired_guest_tokens

# Initialize shared services
room_manager = RoomManager(ConnectionManager(), RoomService())

# Set up shared services in routers
websocket.room_manager = room_manager
debug.room_manager = room_manager


async def check_game_timers():
    """Background task to check for time expiration in all active games."""
    while True:
        try:
            current_time = time.time()
            for room_id, room in room_manager.room_service.rooms.items():
                if room.game.status == GameStatus.IN_PROGRESS:
                    elapsed = current_time - room.game.last_move_time
                    
                    # Check if current player has run out of time
                    if room.game.turn == "white":
                        if room.game.white_time_left - elapsed <= 0:
                            print(f"White player has run out of time in room {room_id}")
                            room.game.white_time_left = 0
                            room.game.status = GameStatus.COMPLETE
                            room.game.completed_at = current_time
                            room.game.winner = "black"
                            await room_manager.emit_game_state_to_room(room_id)
                    else:  # black's turn
                        if room.game.black_time_left - elapsed <= 0:
                            print(f"Black player has run out of time in room {room_id}")
                            room.game.black_time_left = 0
                            room.game.status = GameStatus.COMPLETE
                            room.game.completed_at = current_time
                            room.game.winner = "white"
                            await room_manager.emit_game_state_to_room(room_id)
        except Exception as e:
            print(f"Error in timer check task: {e}")
        
        await asyncio.sleep(1)  # Check every 1 second


async def cleanup_expired_tokens():
    """Background task to clean up expired tokens"""
    while True:
        try:
            expired_refresh = cleanup_expired_refresh_tokens()  # existing function
            expired_guest = cleanup_expired_guest_tokens()    # new function
            if expired_refresh > 0 or expired_guest > 0:
                print(f"Cleaned up {expired_refresh} expired refresh tokens and {expired_guest} expired guest tokens")
        except Exception as e:
            print(f"Error in token cleanup task: {e}")
        
        await asyncio.sleep(3600)  # Run every hour


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    timer_task = asyncio.create_task(check_game_timers())
    cleanup_task = asyncio.create_task(cleanup_expired_tokens())
    room_manager.room_service.start_cleanup_task()
    yield
    # Shutdown
    timer_task.cancel()
    cleanup_task.cancel()
    room_manager.room_service.stop_cleanup_task()


app = FastAPI(
    title="Chess CG API", description="A chess game backend API", version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(websocket.router)
app.include_router(debug.router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
