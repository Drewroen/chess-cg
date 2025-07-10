from app.obj.objects import Position
from app.svc.room import RoomService
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
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
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

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
    await emit_game_state(room_id, websocket, id)
    try:
        while True:
            data = await websocket.receive_json()
            start = Position(data["from"][0], data["from"][1])
            end = Position(data["to"][0], data["to"][1])
            promote_to = data.get("promotion", None)

            room = room_service.get_player_room(id)

            room.game.move(start, end, promote_to)
            for id in [room.white, room.black]:
                if id:
                    connection = manager.active_connections.get(id)
                    if connection:
                        await emit_game_state(room.id, connection, id)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Client left the chat")


async def emit_game_state(room_id, websocket: WebSocket, id: int):
    """Emit the current game state to all players in the room."""
    room = room_service.get_room(room_id)
    state = {
        "id": id,
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
    await websocket.send_json(state)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/abc")
async def get():
    return HTMLResponse(html)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
