"""WebSocket message handler for chess game messages."""

from typing import Dict, Callable, Any
import logging

from app.svc.room import RoomManager
from app.svc.game_service import GameService


class WebSocketMessageHandler:
    """Handles different types of WebSocket messages using strategy pattern."""

    def __init__(self, room_manager):
        self.room_manager: RoomManager = room_manager
        self.game_service = GameService()
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
        from_pos = data["from"]
        to_pos = data["to"]
        promote_to = data.get("promotion", None)

        moved = await self.game_service.process_move(
            room, player_color, from_pos, to_pos, promote_to
        )
        if moved:
            await self.room_manager.emit_game_state_to_room(room.id)
            # Clean up if game completed
            if self.game_service.is_game_complete(room):
                await self.room_manager.cleanup_room_with_elo_update(room.id)

    async def _handle_reset_premove(
        self, _data: Dict[str, Any], room, player_color: str
    ) -> None:
        """Handle reset premove message."""
        await self.game_service.reset_premove(room, player_color)
        # Emit updated game state to show premove cleared
        await self.room_manager.emit_game_state_to_room(room.id)

    async def _handle_resign(
        self, _data: Dict[str, Any], room, player_color: str
    ) -> None:
        """Handle resignation message."""
        game_completed = await self.game_service.process_resignation(room, player_color)
        await self.room_manager.emit_game_state_to_room(room.id)
        # Clean up the room since game is now complete
        if game_completed:
            await self.room_manager.cleanup_room_with_elo_update(room.id)

    async def _handle_draw_request(
        self, _data: Dict[str, Any], room, player_color: str
    ) -> None:
        """Handle draw request message."""
        game_ended = await self.game_service.process_draw_request(room, player_color)
        await self.room_manager.emit_game_state_to_room(room.id)
        # Clean up the room if game ended in a draw
        if game_ended:
            await self.room_manager.cleanup_room_with_elo_update(room.id)
