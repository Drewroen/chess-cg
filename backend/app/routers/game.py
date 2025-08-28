from uuid import UUID
from app.svc.room import RoomManager
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/game", tags=["game"])

# This will be set by main.py
room_manager: RoomManager = None


@router.get("/{room_id}/info")
async def get_game_info(room_id: UUID):
    """Get static game information that doesn't change during gameplay."""
    room = room_manager.room_service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get user info for both players in optimized queries
    white_info = await room_manager.get_user_info(room.white)
    black_info = await room_manager.get_user_info(room.black)
    white_elo = white_info["elo"]
    black_elo = black_info["elo"]
    white_username = white_info["username"]
    black_username = black_info["username"]
    
    return {
        "room_id": str(room.id),
        "players": {
            "white": {
                "id": room.white,
                "name": white_username,
                "elo": white_elo,
            },
            "black": {
                "id": room.black,
                "name": black_username,
                "elo": black_elo,
            },
        },
    }