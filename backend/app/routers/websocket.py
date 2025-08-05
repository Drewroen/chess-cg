from app.svc.room import RoomManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.obj.objects import Position

router = APIRouter()

# These will be set by main.py
room_manager: RoomManager = None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # Extract access token from query parameters
    access_token = token

    connection_id = await room_manager.connect(websocket, access_token)
    user_id = room_manager.manager.connection_id_to_user_id.get(connection_id)
    try:
        while True:
            data = await websocket.receive_json()
            start = Position(data["from"][0], data["from"][1])
            end = Position(data["to"][0], data["to"][1])
            promote_to = data.get("promotion", None)
            room = room_manager.room_service.find_player_room(user_id)
            if room:
                room.game.move(start, end, promote_to)
                await room_manager.emit_game_state_to_room(room.id)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for player {user_id}")
        await room_manager.disconnect(connection_id)
        room = room_manager.room_service.find_player_room(user_id)
        if room:
            await room_manager.emit_game_state_to_room(room.id)
