from uuid import UUID
from app.svc.room import RoomManager
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/debug", tags=["debug"])

# This will be set by main.py
room_manager: RoomManager = None


@router.get("/rooms")
async def get_room():
    room_map = room_manager.room_service.id_to_room_map
    return JSONResponse(
        content=[
            {
                "room_id": room_id,
                "details": {
                    "white": {"id": room.white},
                    "black": {"id": room.black} if room.black else None,
                    "id": str(room.id),
                },
            }
            for room_id, room in room_map.items()
        ],
        status_code=200,
    )


@router.get("/rooms/{room_id}")
async def get_room_by_id(room_id: UUID):
    room = room_manager.room_service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "moves": {
            "white": [
                (x.position_from.coordinates(), x.position_to.coordinates())
                for x in room.game.board.get_available_moves_for_color("white")
            ],
            "black": [
                (x.position_from.coordinates(), x.position_to.coordinates())
                for x in room.game.board.get_available_moves_for_color("black")
            ],
        },
    }
