"""Time management service for chess games."""

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..obj.game import Game, GameStatus


class TimeManager:
    """Handles time tracking and validation for chess games."""

    def update_player_time(self, game: "Game", current_time: float) -> bool:
        """
        Update the current player's time and check for timeout.

        Args:
            game: The game instance to update
            current_time: Current timestamp

        Returns:
            True if game continues, False if player timed out
        """
        from ..obj.game import GameStatus
        
        if game.status != GameStatus.IN_PROGRESS:
            return True

        elapsed = current_time - game.last_move_time

        if game.turn == "white":
            game.white_time_left = max(0, round(game.white_time_left - elapsed, 2))
            if game.white_time_left <= 0:
                self._end_game_by_timeout(game, current_time, "black")
                return False
        else:
            game.black_time_left = max(0, round(game.black_time_left - elapsed, 2))
            if game.black_time_left <= 0:
                self._end_game_by_timeout(game, current_time, "white")
                return False

        return True

    def check_timeout(self, game: "Game", current_time: float) -> bool:
        """
        Check if the current player has timed out without updating the game state.

        Args:
            game: The game instance to check
            current_time: Current timestamp

        Returns:
            True if player has timed out, False otherwise
        """
        from ..obj.game import GameStatus
        
        if game.status != GameStatus.IN_PROGRESS:
            return False

        elapsed = current_time - game.last_move_time

        if game.turn == "white":
            return game.white_time_left - elapsed <= 0
        else:
            return game.black_time_left - elapsed <= 0

    def get_remaining_time(
        self, game: "Game", current_time: float
    ) -> Tuple[float, float]:
        """
        Get remaining time for both players without modifying game state.

        Args:
            game: The game instance
            current_time: Current timestamp

        Returns:
            Tuple of (white_time_remaining, black_time_remaining)
        """
        from ..obj.game import GameStatus
        
        if game.status != GameStatus.IN_PROGRESS:
            return game.white_time_left, game.black_time_left

        elapsed = current_time - game.last_move_time

        if game.turn == "white":
            white_time = max(0, game.white_time_left - elapsed)
            black_time = game.black_time_left
        else:
            white_time = game.white_time_left
            black_time = max(0, game.black_time_left - elapsed)

        return white_time, black_time

    def _end_game_by_timeout(
        self, game: "Game", current_time: float, winner: str
    ) -> None:
        """End the game due to timeout."""
        from ..obj.game import GameStatus
        
        game.status = GameStatus.COMPLETE
        game.completed_at = current_time
        game.winner = winner
        game.end_reason = "time"
