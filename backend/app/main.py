from uuid import UUID
from app.obj.objects import Position
from app.svc.room import RoomService
from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    Request,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

import uvicorn
from typing import Optional

from .auth import (
    GoogleOAuthError,
    exchange_code_for_token,
    get_user_info,
    create_tokens,
    refresh_access_token,
    revoke_refresh_token,
    get_google_auth_url,
    FRONTEND_URL,
    verify_jwt_token,
)
from .models import (
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)

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

        # Create both access and refresh tokens for our application
        access_token, refresh_token = create_tokens(user_info)

        # Redirect to frontend with access token in URL and refresh token as cookie
        redirect_url = f"{FRONTEND_URL}/auth/success?access_token={access_token}"

        response = RedirectResponse(url=redirect_url, status_code=302)

        # Set refresh token as an HTTP-only secure cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # Prevents JavaScript access (XSS protection)
            secure=True,  # Only send over HTTPS in production
            samesite="lax",  # CSRF protection
            max_age=30 * 24 * 60 * 60,  # 30 days in seconds
            path="/",  # Cookie available for entire domain
        )

        return response

    except GoogleOAuthError as e:
        error_msg = f"OAuth authentication failed: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        error_msg = f"Unexpected error during authentication: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)


@app.post("/auth/token", response_model=TokenResponse)
async def get_token_from_code(
    authorization_code: str,
):
    """Exchange authorization code for tokens (JSON response)"""

    try:
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(authorization_code)

        # Get user information from Google
        user_info = await get_user_info(token_data["access_token"])

        # Create both access and refresh tokens for our application
        access_token, refresh_token = create_tokens(user_info)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour in seconds
            user=UserResponse(
                id=user_info["id"],
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info.get("picture"),
            ),
        )

    except GoogleOAuthError as e:
        raise HTTPException(
            status_code=400, detail=f"OAuth authentication failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error during authentication: {str(e)}"
        )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(token: str = Query(..., description="JWT token")):
    """Get current user information from JWT token"""

    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return UserResponse(
        id=payload["sub"],
        email=payload["email"],
        name=payload["name"],
        picture=payload.get("picture"),
    )


@app.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: Request, refresh_request: RefreshTokenRequest = None):
    """Refresh access token using refresh token"""

    # Try to get refresh token from cookie first, then from request body
    refresh_token_value = None

    if refresh_request and refresh_request.refresh_token:
        refresh_token_value = refresh_request.refresh_token
    else:
        # Try to get from cookie
        refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(status_code=400, detail="Refresh token not provided")

    new_access_token = refresh_access_token(refresh_token_value)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return RefreshTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=3600,  # 1 hour in seconds
    )


@app.post("/auth/logout")
async def logout(request: Request, refresh_request: RefreshTokenRequest = None):
    """Logout user by revoking refresh token"""

    # Try to get refresh token from request body first, then from cookie
    refresh_token_value = None

    if refresh_request and refresh_request.refresh_token:
        refresh_token_value = refresh_request.refresh_token
    else:
        # Try to get from cookie
        refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(status_code=400, detail="Refresh token not provided")

    revoked = revoke_refresh_token(refresh_token_value)
    if not revoked:
        raise HTTPException(status_code=400, detail="Refresh token not found")

    response = JSONResponse(content={"message": "Successfully logged out"})

    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token", path="/", httponly=True, secure=True, samesite="lax"
    )

    return response


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
room_service = RoomService()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    id = await manager.connect(websocket, websocket.query_params.get("token", None))
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
