from uuid import UUID
from app.svc.room import RoomManager
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session
from app.svc.database_service import DatabaseService
from app.auth import verify_jwt_token
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


# Pydantic models for loadout endpoint
class PiecePosition(BaseModel):
    row: int
    col: int


class PieceLoadout(BaseModel):
    color: str
    piece_type: str
    position: PiecePosition
    modifiers: list[str]


class LoadoutRequest(BaseModel):
    loadout: list[PieceLoadout]


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


@router.post("/loadout/validate")
async def validate_loadout(loadout_request: LoadoutRequest):
    """Validate a piece loadout with modifiers."""

    # Map of all modifiers by type for quick lookup
    all_modifiers_map = {
        # Rook modifiers
        "Knook": KNOOK_MODIFIER,
        "Kitty Castle": DIAGONAL_ROOK_MODIFIER,
        "Quook": QUOOK_MODIFIER,
        # Pawn modifiers
        "Reverse": BACKWARDS_PAWN_MODIFIER,
        "Kitty": DIAGONAL_PAWN_MODIFIER,
        "Long Leaper": LONG_LEAP_PAWN_MODIFIER,
        # Bishop modifiers
        "Sidestepper": SIDESTEP_BISHOP_MODIFIER,
        "Unicorn": UNICORN_MODIFIER,
        "Corner Hop": CORNER_HOP_MODIFIER,
        # Knight modifiers
        "Longhorn": LONGHORN_MODIFIER,
        "Pegasus": PEGASUS_MODIFIER,
        "Royal Guard": ROYAL_GUARD_MODIFIER,
        # Queen modifiers
        "Sacrificial Lamb": SACRIFICIAL_QUEEN_MODIFIER,
        "Kneen": KNEEN_MODIFIER,
        "Infiltration": INFILTRATION_MODIFIER,
        # King modifiers
        "Escape Hatch": ESCAPE_HATCH_MODIFIER,
        "Aggression": AGGRESSIVE_KING_MODIFIER,
        "Teleport": TELEPORT_MODIFIER,
    }

    # Valid starting positions for each piece type and color
    # White: row 7 (back rank), row 6 (pawns)
    # Black: row 0 (back rank), row 1 (pawns)
    valid_positions = {
        "white": {
            "pawn": [(6, col) for col in range(8)],
            "rook": [(7, 0), (7, 7)],
            "knight": [(7, 1), (7, 6)],
            "bishop": [(7, 2), (7, 5)],
            "queen": [(7, 3)],
            "king": [(7, 4)],
        },
        "black": {
            "pawn": [(1, col) for col in range(8)],
            "rook": [(0, 0), (0, 7)],
            "knight": [(0, 1), (0, 6)],
            "bishop": [(0, 2), (0, 5)],
            "queen": [(0, 3)],
            "king": [(0, 4)],
        },
    }

    errors = []

    for piece_loadout in loadout_request.loadout:
        color = piece_loadout.color
        piece_type = piece_loadout.piece_type
        position = (piece_loadout.position.row, piece_loadout.position.col)
        modifiers = piece_loadout.modifiers

        # Validate color
        if color not in ["white", "black"]:
            errors.append(f"Invalid color '{color}' for piece at {position}")
            continue

        # Validate piece type
        if piece_type not in valid_positions[color]:
            errors.append(f"Invalid piece type '{piece_type}' for color '{color}'")
            continue

        # Validate position
        if position not in valid_positions[color][piece_type]:
            errors.append(
                f"{color.capitalize()} {piece_type} cannot be at position {position}. "
                f"Valid positions: {valid_positions[color][piece_type]}"
            )

        # Validate modifiers
        for modifier_type in modifiers:
            if modifier_type not in all_modifiers_map:
                errors.append(f"Unknown modifier '{modifier_type}'")
                continue

            modifier = all_modifiers_map[modifier_type]
            if not modifier.can_apply_to_piece(piece_type):
                errors.append(
                    f"Modifier '{modifier_type}' cannot be applied to {piece_type}. "
                    f"Applicable to: {modifier.applicable_piece}"
                )

    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    # If validation passes, print and return success
    print("Loadout validation passed!")
    print(f"Received loadout: {loadout_request.model_dump_json(indent=2)}")

    return {
        "status": "valid",
        "message": "Loadout is valid",
        "loadout": loadout_request.model_dump(),
    }


@router.get("/loadout")
async def get_loadout(
    request: Request, db_session: AsyncSession = Depends(get_db_session)
):
    """Get the piece loadout with modifiers for the authenticated user."""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    # Verify the token is valid
    payload = verify_jwt_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload["sub"]

    # Fetch the user's loadout from the database
    db_service = DatabaseService(db_session)
    user = await db_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the loadout (or null if not set)
    return {"loadout": user.loadout}


@router.post("/loadout/save")
async def save_loadout(
    loadout_request: LoadoutRequest,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Save a piece loadout with modifiers for the authenticated user."""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    # Verify the token is valid
    payload = verify_jwt_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload["sub"]

    # Validate the loadout first (reuse validation logic from validate endpoint)
    all_modifiers_map = {
        # Rook modifiers
        "Knook": KNOOK_MODIFIER,
        "Kitty Castle": DIAGONAL_ROOK_MODIFIER,
        "Quook": QUOOK_MODIFIER,
        # Pawn modifiers
        "Reverse": BACKWARDS_PAWN_MODIFIER,
        "Kitty": DIAGONAL_PAWN_MODIFIER,
        "Long Leaper": LONG_LEAP_PAWN_MODIFIER,
        # Bishop modifiers
        "Sidestepper": SIDESTEP_BISHOP_MODIFIER,
        "Unicorn": UNICORN_MODIFIER,
        "Corner Hop": CORNER_HOP_MODIFIER,
        # Knight modifiers
        "Longhorn": LONGHORN_MODIFIER,
        "Pegasus": PEGASUS_MODIFIER,
        "Royal Guard": ROYAL_GUARD_MODIFIER,
        # Queen modifiers
        "Sacrificial Lamb": SACRIFICIAL_QUEEN_MODIFIER,
        "Kneen": KNEEN_MODIFIER,
        "Infiltration": INFILTRATION_MODIFIER,
        # King modifiers
        "Escape Hatch": ESCAPE_HATCH_MODIFIER,
        "Aggression": AGGRESSIVE_KING_MODIFIER,
        "Teleport": TELEPORT_MODIFIER,
    }

    valid_positions = {
        "white": {
            "pawn": [(6, col) for col in range(8)],
            "rook": [(7, 0), (7, 7)],
            "knight": [(7, 1), (7, 6)],
            "bishop": [(7, 2), (7, 5)],
            "queen": [(7, 3)],
            "king": [(7, 4)],
        },
        "black": {
            "pawn": [(1, col) for col in range(8)],
            "rook": [(0, 0), (0, 7)],
            "knight": [(0, 1), (0, 6)],
            "bishop": [(0, 2), (0, 5)],
            "queen": [(0, 3)],
            "king": [(0, 4)],
        },
    }

    errors = []

    for piece_loadout in loadout_request.loadout:
        color = piece_loadout.color
        piece_type = piece_loadout.piece_type
        position = (piece_loadout.position.row, piece_loadout.position.col)
        modifiers = piece_loadout.modifiers

        # Validate color
        if color not in ["white", "black"]:
            errors.append(f"Invalid color '{color}' for piece at {position}")
            continue

        # Validate piece type
        if piece_type not in valid_positions[color]:
            errors.append(f"Invalid piece type '{piece_type}' for color '{color}'")
            continue

        # Validate position
        if position not in valid_positions[color][piece_type]:
            errors.append(
                f"{color.capitalize()} {piece_type} cannot be at position {position}. "
                f"Valid positions: {valid_positions[color][piece_type]}"
            )

        # Validate modifiers
        for modifier_type in modifiers:
            if modifier_type not in all_modifiers_map:
                errors.append(f"Unknown modifier '{modifier_type}'")
                continue

            modifier = all_modifiers_map[modifier_type]
            if not modifier.can_apply_to_piece(piece_type):
                errors.append(
                    f"Modifier '{modifier_type}' cannot be applied to {piece_type}. "
                    f"Applicable to: {modifier.applicable_piece}"
                )

    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    # Save the loadout to the database
    db_service = DatabaseService(db_session)
    user = await db_service.update_user_loadout(user_id, loadout_request.model_dump())

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "message": "Loadout saved successfully",
        "loadout": loadout_request.model_dump(),
    }
