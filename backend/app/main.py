from uuid import UUID
from app.obj.objects import Position
from app.svc.room import RoomService
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

import uvicorn
from typing import Optional

from .auth import (
    GoogleOAuthError,
    exchange_code_for_token,
    get_user_info,
    create_jwt_token,
    get_google_auth_url,
    FRONTEND_URL,
)
from .models import UserResponse

app = FastAPI(
    title="Chess CG API", description="A chess game backend API", version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Chess CG API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        auth_url = get_google_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Google auth URL: {str(e)}"
        )


@app.get("/auth/callback")
async def auth_callback(
    code: Optional[str] = Query(None, description="Authorization code from Google"),
    error: Optional[str] = Query(None, description="Error from Google OAuth"),
    state: Optional[str] = Query(None, description="State parameter"),
):
    """Handle Google OAuth callback"""

    # Check for OAuth errors
    if error:
        error_msg = f"Google OAuth error: {error}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)

    # Check for missing authorization code
    if not code:
        error_msg = "Missing authorization code"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)

    try:
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(code)

        # Get user information from Google
        user_info = await get_user_info(token_data["access_token"])

        # Create JWT token for our application
        jwt_token = create_jwt_token(user_info)

        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/auth/success?token={jwt_token}"

        return RedirectResponse(url=redirect_url, status_code=302)

    except GoogleOAuthError as e:
        error_msg = f"OAuth authentication failed: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        error_msg = f"Unexpected error during authentication: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(token: str = Query(..., description="JWT token")):
    """Get current user information from JWT token"""
    from .auth import verify_jwt_token

    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return UserResponse(
        id=payload["sub"],
        email=payload["email"],
        name=payload["name"],
        picture=payload.get("picture"),
    )


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.next_id = 1

    async def connect(self, websocket: WebSocket) -> int:
        await websocket.accept()
        connection_id = self.next_id
        self.active_connections[connection_id] = websocket
        self.next_id += 1
        return connection_id

    def disconnect(self, connection_id: int):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Failed to send personal message: {e}")

    async def broadcast(self, message: str):
        disconnected_connections = []
        for connection_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(
                    f"Failed to send broadcast message to connection {connection_id}: {e}"
                )
                disconnected_connections.append(connection_id)

        # Remove disconnected connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)

    def is_connection_active(self, connection_id: int) -> bool:
        """Check if a connection is still active"""
        return connection_id in self.active_connections

    def get_active_connections(self):
        return [
            {"id": connection_id, "websocket": websocket}
            for connection_id, websocket in self.active_connections.items()
        ]


manager = ConnectionManager()
room_service = RoomService()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    id = await manager.connect(websocket)
    room_id = room_service.add(id)
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
    room = room_service.get_room(room_id)
    if room:
        state = {
            "squares": room.game.board.get_squares(),
            "turn": room.game.turn,
            "players": {
                "white": room.white,
                "black": room.black,
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
                    await connection.send_json(state)


@app.get("/debug/rooms")
async def get_room():
    room_map = room_service.id_to_room_map
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


@app.get("/debug/rooms/{room_id}")
async def get_room_by_id(room_id: UUID):
    print(room_service.rooms)
    room = room_service.get_room(room_id)
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


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
