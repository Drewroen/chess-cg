from app.svc.room import RoomManager
from app.svc.websocket_handler import WebSocketMessageHandler
from app.obj.game import GameStatus
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import time

router = APIRouter()

# These will be set by main.py
room_manager: RoomManager = None
message_handler: WebSocketMessageHandler = None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # Extract access token from query parameters
    access_token = token

    connection_id = await room_manager.connect(websocket, access_token)
    user_id = room_manager.manager.connection_id_to_user_id.get(connection_id)
    try:
        while True:
            data = await websocket.receive_json()
            room = room_manager.room_service.find_player_room(user_id)
            if room:
                player_color = "white" if room.white == user_id else "black"

                # Route message to appropriate handler
                await message_handler.handle_message(data, room, player_color)

    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected for player {user_id}")
        await room_manager.disconnect(connection_id)
        room = room_manager.room_service.find_player_room(user_id)
        if room:
            # If game hasn't started yet and a player disconnects, abort the game
            if room.game.status == GameStatus.NOT_STARTED:
                room.game.status = GameStatus.ABORTED
                room.game.end_reason = "aborted"
                room.game.completed_at = time.time()
                room.game.winner = "aborted"
                logging.info(
                    f"Aborted game {room.id} due to player {user_id} disconnect before game start"
                )
                await room_manager.emit_game_state_to_room(room.id)
                await room_manager.cleanup_room_with_elo_update(room.id)
            else:
                await room_manager.emit_game_state_to_room(room.id)
