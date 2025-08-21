from app.svc.room import RoomManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.obj.objects import Position
from app.obj.game import GameStatus

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
            room = room_manager.room_service.find_player_room(user_id)
            if room:
                # Determine player color
                player_color = "white" if room.white == user_id else "black"

                # Route message based on type
                message_type = data.get("type")

                if message_type == "move":
                    # Handle move message
                    start = Position(data["from"][0], data["from"][1])
                    end = Position(data["to"][0], data["to"][1])
                    promote_to = data.get("promotion", None)
                    moved = room.game.move(start, end, player_color, promote_to)
                    if moved:
                        await room_manager.emit_game_state_to_room(room.id)
                        # Clean up if game completed
                        if room.game.status == GameStatus.COMPLETE:
                            await room_manager.cleanup_room_with_elo_update(room.id)

                elif message_type == "reset_premove":
                    # Handle reset premove message
                    if player_color == "white":
                        room.game.white_premove = None
                    else:
                        room.game.black_premove = None
                    # Emit updated game state to show premove cleared
                    await room_manager.emit_game_state_to_room(room.id)

                elif message_type == "resign":
                    # Handle resignation
                    if room.game.status == GameStatus.IN_PROGRESS:
                        room.game.mark_player_forfeit(player_color)
                        await room_manager.emit_game_state_to_room(room.id)
                        # Clean up the room since game is now complete
                        if room.game.status == GameStatus.COMPLETE:
                            await room_manager.cleanup_room_with_elo_update(room.id)

                elif message_type == "request_draw":
                    # Handle draw request
                    if room.game.status == GameStatus.IN_PROGRESS:
                        game_ended = room.game.request_draw(player_color)
                        await room_manager.emit_game_state_to_room(room.id)
                        # Clean up the room if game ended in a draw
                        if game_ended and room.game.status == GameStatus.COMPLETE:
                            await room_manager.cleanup_room_with_elo_update(room.id)

                else:
                    print(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for player {user_id}")
        await room_manager.disconnect(connection_id)
        room = room_manager.room_service.find_player_room(user_id)
        if room:
            await room_manager.emit_game_state_to_room(room.id)
