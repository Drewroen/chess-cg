from uuid import UUID
from app.svc.room import RoomManager
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.obj.modifier import (
    KNOOK_MODIFIER,
    DIAGONAL_ROOK_MODIFIER,
    QUOOK_MODIFIER,
    BACKWARDS_PAWN_MODIFIER,
    DIAGONAL_PAWN_MODIFIER,
    LONG_LEAP_PAWN_MODIFIER,
    SIDESTEP_BISHOP_MODIFIER,
    UNICORN_MODIFIER,
    CORNER_HOP_MODIFIER,
    LONGHORN_MODIFIER,
    PEGASUS_MODIFIER,
    ROYAL_GUARD_MODIFIER,
    SACRIFICIAL_QUEEN_MODIFIER,
    KNEEN_MODIFIER,
    INFILTRATION_MODIFIER,
    ESCAPE_HATCH_MODIFIER,
    AGGRESSIVE_KING_MODIFIER,
    TELEPORT_MODIFIER,
)

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


@router.get("/modifiers")
async def get_available_modifiers():
    """Get all available piece modifiers."""
    all_modifiers = [
        # Rook modifiers
        KNOOK_MODIFIER,
        DIAGONAL_ROOK_MODIFIER,
        QUOOK_MODIFIER,
        # Pawn modifiers
        BACKWARDS_PAWN_MODIFIER,
        DIAGONAL_PAWN_MODIFIER,
        LONG_LEAP_PAWN_MODIFIER,
        # Bishop modifiers
        SIDESTEP_BISHOP_MODIFIER,
        UNICORN_MODIFIER,
        CORNER_HOP_MODIFIER,
        # Knight modifiers
        LONGHORN_MODIFIER,
        PEGASUS_MODIFIER,
        ROYAL_GUARD_MODIFIER,
        # Queen modifiers
        SACRIFICIAL_QUEEN_MODIFIER,
        KNEEN_MODIFIER,
        INFILTRATION_MODIFIER,
        # King modifiers
        ESCAPE_HATCH_MODIFIER,
        AGGRESSIVE_KING_MODIFIER,
        TELEPORT_MODIFIER,
    ]

    return {"modifiers": [modifier.to_dict() for modifier in all_modifiers]}
