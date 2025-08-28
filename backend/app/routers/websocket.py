from app.svc.room import RoomManager
from app.svc.websocket_handler import WebSocketMessageHandler
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

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
            await room_manager.emit_game_state_to_room(room.id)
