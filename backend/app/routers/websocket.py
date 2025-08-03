from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.obj.objects import Position
from ..auth import verify_jwt_token

router = APIRouter()


class WebSocketConnection:
    def __init__(self, websocket: WebSocket, jwt: str):
        self.websocket = websocket
        self.jwt = jwt
        payload = None
        if jwt:
            payload = verify_jwt_token(jwt)
        self.name = payload.get("name", "Guest") if payload else "Guest"


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocketConnection] = {}
        self.next_id = 1

    async def connect(self, websocket: WebSocket, jwt: str = None) -> int:
        await websocket.accept()
        connection_id = self.next_id
        self.active_connections[connection_id] = WebSocketConnection(websocket, jwt)
        self.next_id += 1
        return connection_id

    def disconnect(self, connection_id: int):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

    def is_connection_active(self, connection_id: int) -> bool:
        """Check if a connection is still active"""
        return connection_id in self.active_connections

    def get_active_connections(self):
        return [
            {"id": connection_id, "websocket": websocket}
            for connection_id, websocket in self.active_connections.items()
        ]


manager = ConnectionManager()

# These will be set by main.py
room_service = None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # Extract access token from query parameters
    access_token = token

    id = await manager.connect(websocket, access_token)
    room_id = room_service.add(id)
    if room_service.is_room_full(room_id):
        await emit_game_state_to_room(room_id)
    try:
        while True:
            data = await websocket.receive_json()
            start = Position(data["from"][0], data["from"][1])
            end = Position(data["to"][0], data["to"][1])
            promote_to = data.get("promotion", None)

            room = room_service.get_player_room(id)

            room.game.move(start, end, promote_to)
            # Only send game state to active connections
            for player_id in [room.white, room.black]:
                if player_id and manager.is_connection_active(player_id):
                    connection = manager.active_connections.get(player_id)
                    if connection:
                        await emit_game_state_to_room(room.id)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for player {id}")
        manager.disconnect(id)
        room_service.disconnect(id)
        await emit_game_state_to_room(room_id)
    except Exception as e:
        print(f"WebSocket error for player {id}: {e}")
        manager.disconnect(id)
        room_service.disconnect(id)
        await emit_game_state_to_room(room_id)


async def emit_game_state_to_room(room_id):
    """Emit the current game state to all players in the room."""
    global room_service, manager

    room = room_service.get_room(room_id)
    if room:
        state = {
            "squares": room.game.board.get_squares(),
            "turn": room.game.turn,
            "players": {
                "white": {
                    "id": room.white,
                    "name": manager.active_connections.get(room.white).name
                    if room.white in manager.active_connections
                    else "Disconnected",
                    "connected": manager.is_connection_active(room.white),
                },
                "black": {
                    "id": room.black,
                    "name": manager.active_connections.get(room.black).name
                    if room.black in manager.active_connections
                    else "Disconnected",
                    "connected": manager.is_connection_active(room.black),
                },
            },
            "kings_in_check": room.game.board.kings_in_check(),
            "status": room.game.status.value,
            "time": {
                "white": room.game.white_time_left,
                "black": room.game.black_time_left,
            },
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
        for player_id in [room.white, room.black]:
            state["id"] = player_id
            if player_id and manager.is_connection_active(player_id):
                connection = manager.active_connections.get(player_id)
                if connection:
                    await connection.websocket.send_json(state)
