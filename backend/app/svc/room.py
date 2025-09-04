from uuid import UUID, uuid4
from app.obj.game import Game, GameStatus
from fastapi import WebSocket
from ..auth import verify_jwt_token
from ..database import get_db_session
from ..svc.database_service import DatabaseService
from ..svc.elo_service import EloService
import time
import logging


class WebSocketConnection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.id = uuid4()


class ConnectionManager:
    def __init__(self):
        self.id_to_websocket_connection: dict[UUID, WebSocketConnection] = {}
        self.user_id_to_connection_map: dict[str, list[WebSocketConnection]] = {}
        self.connection_id_to_user_id: dict[UUID, str] = {}
        self.user_id_to_name: dict[str, str] = {}

    async def connect(self, websocket: WebSocket, jwt: str = None) -> str:
        await websocket.accept()

        # Extract name from JWT or generate guest name
        token_data = verify_jwt_token(jwt)
        if token_data and "sub" in token_data:
            user_id = token_data["sub"]
            name = token_data["name"]
        else:
            user_id = "guest_" + str(uuid4())
            name = "Guest"

        # Create connection
        connection = WebSocketConnection(websocket)
        self.id_to_websocket_connection[connection.id] = connection

        # Add to name mapping
        if user_id not in self.user_id_to_connection_map:
            self.user_id_to_connection_map[user_id] = []
            self.user_id_to_name[user_id] = name
        self.user_id_to_connection_map[user_id].append(connection)

        # Track connection ID to name for cleanup
        self.connection_id_to_user_id[connection.id] = user_id

        return connection.id

    def get_user_id_for_connection(self, connection_id) -> str:
        """Return user_id for a given connection ID"""
        return self.connection_id_to_user_id.get(connection_id)


class Room:
    def __init__(self):
        self.id = uuid4()
        self.white: str
        self.black: str
        self.game: Game = Game()


class RoomService:
    def __init__(self):
        self.rooms: dict[UUID, Room] = {}
        self.queue: list[str] = []
        self.player_to_room_map: dict[str, UUID] = {}

    def add_to_queue(self, name: str):
        """Add a player to the queue if not already present."""
        if name not in self.queue:
            self.queue.append(name)

    def queue_length(self) -> int:
        """Return the number of players in the queue."""
        return len(self.queue)

    def new_room(self, white: str, black: str) -> UUID:
        """Create a new room with the given players."""
        room = Room()
        room.white = white
        room.black = black
        self.rooms[room.id] = room

        if white in self.queue:
            self.queue.remove(white)
            self.player_to_room_map[white] = room.id
        if black in self.queue:
            self.queue.remove(black)
            self.player_to_room_map[black] = room.id

        return room.id

    def find_player_room(self, player_name: str) -> Room:
        """Find the room ID for a given player."""
        room_id = self.player_to_room_map.get(player_name)
        if not room_id:
            return None
        return self.rooms[room_id]

    def get_room(self, room_id: UUID) -> Room:
        """Get a room by its ID."""
        return self.rooms.get(room_id)

    async def cleanup_room(self, room_id: UUID):
        """Remove a completed game and clean up player mappings."""
        if room_id not in self.rooms:
            return

        room = self.rooms[room_id]

        # Save game to database if it was completed or aborted
        if room.game.status in [GameStatus.COMPLETE, GameStatus.ABORTED]:
            try:
                async for session in get_db_session():
                    db_service = DatabaseService(session)
                    winner = (
                        room.game.winner
                        if room.game.status == GameStatus.COMPLETE
                        else "aborted"
                    )
                    end_reason = (
                        room.game.end_reason
                        if room.game.status == GameStatus.COMPLETE
                        else "aborted"
                    )
                    # Convert guest player IDs to None for database storage
                    white_db_id = (
                        None if room.white.startswith("guest_") else room.white
                    )
                    black_db_id = (
                        None if room.black.startswith("guest_") else room.black
                    )

                    await db_service.create_chess_game(
                        white_player_id=white_db_id,
                        black_player_id=black_db_id,
                        winner=winner,
                        end_reason=end_reason,
                    )

                    status_text = (
                        "completed"
                        if room.game.status == GameStatus.COMPLETE
                        else "aborted"
                    )
                    logging.info(f"Saved {status_text} game {room_id} to database")
            except Exception as e:
                logging.error(f"Error saving game {room_id} to database: {e}")

        # Clean up player mappings
        if room.white in self.player_to_room_map:
            del self.player_to_room_map[room.white]
        if room.black in self.player_to_room_map:
            del self.player_to_room_map[room.black]
        # Remove the room
        del self.rooms[room_id]
        logging.info(f"Cleaned up completed game {room_id}")


class RoomManager:
    def __init__(self, manager: ConnectionManager, room_service: RoomService):
        self.room_service = room_service
        self.manager = manager
        self.elo_service = EloService()

    async def get_user_info(self, user_id: str) -> dict:
        """Get user info (ELO and username) in a single query."""
        if not user_id or user_id.startswith("guest_"):
            return {"elo": None, "username": "Guest"}

        try:
            async for session in get_db_session():
                db_service = DatabaseService(session)
                user = await db_service.get_user_by_id(user_id)
                return {
                    "elo": user.elo if user else None,
                    "username": user.username if user and user.username else "Guest",
                }
        except Exception as e:
            logging.error(f"Error fetching user info for user {user_id}: {e}")
            return {"elo": None, "username": "Guest"}

    async def get_user_elo(self, user_id: str) -> int:
        """Get the ELO rating for a user."""
        user_info = await self.get_user_info(user_id)
        return user_info["elo"]

    async def get_user_username(self, user_id: str) -> str:
        """Get the username for a user."""
        user_info = await self.get_user_info(user_id)
        return user_info["username"]

    async def cleanup_room_with_elo_update(self, room_id: UUID):
        """Clean up a room and update ELO ratings if the game was completed."""
        if room_id not in self.room_service.rooms:
            return

        room = self.room_service.rooms[room_id]

        # Update ELO ratings for completed games before cleanup
        if room.game.status == GameStatus.COMPLETE:
            try:
                async for session in get_db_session():
                    db_service = DatabaseService(session)
                    await self.elo_service.update_ratings(
                        room.white,
                        room.black,
                        room.game.winner,
                        self.get_user_info,
                        db_service,
                    )
            except Exception as e:
                logging.error(f"Error updating ELO ratings for room {room_id}: {e}")

        # Now clean up the room
        await self.room_service.cleanup_room(room_id)

    async def connect(self, websocket, jwt: str = None) -> str:
        """Connect a player to the WebSocket and return their name."""
        connection_id = await self.manager.connect(websocket, jwt)
        name = self.manager.connection_id_to_user_id.get(connection_id)
        existing_room = self.room_service.find_player_room(name)
        if existing_room:
            await self.emit_game_state_to_room(existing_room.id)
        else:
            # If the player is not already in a room, add them to the queue
            self.room_service.add_to_queue(name)
            if self.room_service.queue_length() >= 2:
                room_id = self.room_service.new_room(
                    self.room_service.queue[0], self.room_service.queue[1]
                )
                await self.emit_game_state_to_room(room_id)

        return connection_id

    async def disconnect(self, connection_id: UUID):
        """Disconnect a player by connection ID."""
        user_id = self.manager.connection_id_to_user_id.get(connection_id)
        if user_id and connection_id in self.manager.id_to_websocket_connection:
            # Remove the specific connection
            connection = self.manager.id_to_websocket_connection[connection_id]
            if user_id in self.manager.user_id_to_connection_map:
                self.manager.user_id_to_connection_map[user_id].remove(connection)
                # Clean up empty lists
                if not self.manager.user_id_to_connection_map[user_id]:
                    del self.manager.user_id_to_connection_map[user_id]
            del self.manager.id_to_websocket_connection[connection_id]
            del self.manager.connection_id_to_user_id[connection_id]

    async def emit_game_state_to_room(self, room_id: UUID):
        """Emit the current game state to all players in the room."""
        if not room_id:
            return
        room = self.room_service.rooms[room_id]

        if room:
            state = {
                "squares": room.game.board.get_squares(),
                "turn": room.game.turn,
                "kings_in_check": room.game.board.kings_in_check(),
                "status": room.game.status.value,
                "winner": room.game.winner,
                "end_reason": room.game.end_reason,
                "time": {
                    "white": self._get_current_time_remaining(room.game, "white"),
                    "black": self._get_current_time_remaining(room.game, "black"),
                },
                "draw_requests": {
                    "white": room.game.white_draw_requested,
                    "black": room.game.black_draw_requested,
                },
                "captured_pieces": room.game.captured_pieces,
                "last_move": room.game.last_move.to_dict()
                if room.game.last_move
                else None,
            }
        for player_name in [room.white, room.black]:
            state["id"] = str(room.id)  # Room ID for fetching game info
            state["player_id"] = (
                player_name  # Player ID to identify which player this is
            )

            # Determine player color
            player_color = "white" if player_name == room.white else "black"

            # Add turn-based moves: regular moves if it's their turn, premoves if not
            if room.game.turn == player_color:
                state["moves"] = [
                    x.to_dict()
                    for x in room.game.board.get_available_moves_for_color(player_color)
                ]
            else:
                state["moves"] = [
                    x.to_dict()
                    for x in room.game.board.get_available_premoves_for_color(
                        player_color
                    )
                ]

            # Add opponent connection status
            opponent_name = room.black if player_name == room.white else room.white
            state["opponent_connected"] = (
                len(self.manager.user_id_to_connection_map.get(opponent_name, [])) > 0
            )

            connections = self.manager.user_id_to_connection_map.get(player_name, [])
            for connection in connections:
                if (
                    connection
                    and self.manager.get_user_id_for_connection(connection.id)
                    is not None
                ):
                    try:
                        await connection.websocket.send_json(state)
                    except Exception as e:
                        logging.error(f"Failed to send to {player_name}: {e}")

    def _get_current_time_remaining(self, game, player_color):
        """Calculate the current time remaining for a player, accounting for elapsed time since last move."""
        base_time = (
            game.white_time_left if player_color == "white" else game.black_time_left
        )
        if game.status != GameStatus.IN_PROGRESS:
            # If game is not in progress, return the stored time
            return base_time

        # If it's this player's turn, subtract elapsed time since last move
        if game.turn == player_color:
            current_time = time.time()
            elapsed_since_last_move = current_time - game.last_move_time
            current_time_remaining = max(0, base_time - elapsed_since_last_move)
            return round(current_time_remaining, 2)
        else:
            # If it's not this player's turn, return their stored time
            return base_time
