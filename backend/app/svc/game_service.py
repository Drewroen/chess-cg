"""Game service for handling chess game business logic."""

from typing import Optional, Tuple

from app.svc.room import Room

from ..obj.game import GameStatus
from ..obj.position import Position


class GameService:
    """Service for handling chess game business logic operations."""

    async def process_move(
        self,
        room: Room,
        player_color: str,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        promotion: Optional[str] = None,
    ) -> bool:
        """
        Process a chess move for a player.

        Args:
            room: The game room
            player_color: Player's color ("white" or "black")
            from_pos: Starting position tuple (row, col)
            to_pos: Ending position tuple (row, col)
            promotion: Promotion piece if applicable

        Returns:
            True if move was successful, False otherwise
        """
        start = Position(from_pos[0], from_pos[1])
        end = Position(to_pos[0], to_pos[1])

        return room.game.move(start, end, player_color, promotion)

    async def process_resignation(self, room: Room, player_color: str) -> bool:
        """
        Process a player resignation.

        Args:
            room: The game room
            player_color: Player's color ("white" or "black")

        Returns:
            True if resignation was processed, False if game not in progress
        """
        if room.game.status != GameStatus.IN_PROGRESS:
            return False

        room.game.mark_player_forfeit(player_color)
        return True

    async def process_draw_request(self, room: Room, player_color: str) -> bool:
        """
        Process a draw request from a player.

        Args:
            room: The game room
            player_color: Player's color ("white" or "black")

        Returns:
            True if draw was accepted and game ended, False otherwise
        """
        if room.game.status != GameStatus.IN_PROGRESS:
            return False

        game_ended = room.game.request_draw(player_color)
        return game_ended

    async def reset_premove(self, room: Room, player_color: str) -> None:
        """
        Reset the premove for a player.

        Args:
            room: The game room
            player_color: Player's color ("white" or "black")
        """
        if player_color == "white":
            room.game.white_premove = None
        else:
            room.game.black_premove = None

    def is_game_complete(self, room: Room) -> bool:
        """
        Check if the game is complete.

        Args:
            room: The game room

        Returns:
            True if game is complete, False otherwise
        """
        return room.game.status == GameStatus.COMPLETE
