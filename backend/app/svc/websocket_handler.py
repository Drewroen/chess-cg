"""WebSocket message handler for chess game messages."""

from typing import Dict, Callable, Any
import logging

from app.svc.room import RoomManager
from ..obj.game import GameStatus
from ..obj.chess import Position


class WebSocketMessageHandler:
    """Handles different types of WebSocket messages using strategy pattern."""

    def __init__(self, room_manager):
        self.room_manager: RoomManager = room_manager
        self.handlers: Dict[str, Callable] = {
            "move": self._handle_move,
            "reset_premove": self._handle_reset_premove,
            "resign": self._handle_resign,
            "request_draw": self._handle_draw_request,
        }

    async def handle_message(
        self, data: Dict[str, Any], room, player_color: str
    ) -> None:
        """
        Route message to appropriate handler based on type.

        Args:
            data: The message data
            room: The room instance
            player_color: The player's color ("white" or "black")
        """
        message_type = data.get("type")
        handler = self.handlers.get(message_type)

        if handler:
            await handler(data, room, player_color)
        else:
            logging.warning(f"Unknown message type: {message_type}")

    async def _handle_move(self, data: Dict[str, Any], room, player_color: str) -> None:
        """Handle move message."""
        start = Position(data["from"][0], data["from"][1])
        end = Position(data["to"][0], data["to"][1])
        promote_to = data.get("promotion", None)

        moved = room.game.move(start, end, player_color, promote_to)
        if moved:
            await self.room_manager.emit_game_state_to_room(room.id)
            # Clean up if game completed
            if room.game.status == GameStatus.COMPLETE:
                await self.room_manager.cleanup_room_with_elo_update(room.id)

    async def _handle_reset_premove(
        self, data: Dict[str, Any], room, player_color: str
    ) -> None:
        """Handle reset premove message."""
        if player_color == "white":
            room.game.white_premove = None
        else:
            room.game.black_premove = None

        # Emit updated game state to show premove cleared
        await self.room_manager.emit_game_state_to_room(room.id)

    async def _handle_resign(
        self, data: Dict[str, Any], room, player_color: str
    ) -> None:
        """Handle resignation message."""
        if room.game.status == GameStatus.IN_PROGRESS:
            room.game.mark_player_forfeit(player_color)
            await self.room_manager.emit_game_state_to_room(room.id)
            # Clean up the room since game is now complete
            if room.game.status == GameStatus.COMPLETE:
                await self.room_manager.cleanup_room_with_elo_update(room.id)

    async def _handle_draw_request(
        self, data: Dict[str, Any], room, player_color: str
    ) -> None:
        """Handle draw request message."""
        if room.game.status == GameStatus.IN_PROGRESS:
            game_ended = room.game.request_draw(player_color)
            await self.room_manager.emit_game_state_to_room(room.id)
            # Clean up the room if game ended in a draw
            if game_ended and room.game.status == GameStatus.COMPLETE:
                await self.room_manager.cleanup_room_with_elo_update(room.id)
