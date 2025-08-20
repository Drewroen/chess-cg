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
    
    # Get ELO ratings for both players
    white_elo = await room_manager.get_user_elo(room.white)
    black_elo = await room_manager.get_user_elo(room.black)
    
    return {
        "room_id": str(room.id),
        "players": {
            "white": {
                "id": room.white,
                "name": room_manager.manager.user_id_to_name.get(room.white, "Guest"),
                "elo": white_elo,
            },
            "black": {
                "id": room.black,
                "name": room_manager.manager.user_id_to_name.get(room.black, "Guest"),
                "elo": black_elo,
            },
        },
    }