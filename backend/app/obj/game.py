from enum import Enum
from app.obj.board import Board
from app.svc.time_manager import TimeManager
import time
import logging


class GameStatus(Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"
    ABORTED = "aborted"


STARTING_TIME_IN_SECONDS = 180.0
MOVE_INCREMENT_IN_SECONDS = 2.0
PREMOVE_PENALTY_IN_SECONDS = 0.1
GAME_START_TIMEOUT_SECONDS = 20.0


class Game:
    def __init__(self):
        self.turn = "white"
        self.board = Board()
        self.status = GameStatus.NOT_STARTED
        self.white_time_left = STARTING_TIME_IN_SECONDS
        self.black_time_left = STARTING_TIME_IN_SECONDS
        self.last_move_time = time.time()
        self.created_at = time.time()
        self.winner = None
        self.end_reason = None
        self.white_premove = None
        self.black_premove = None
        self.completed_at = None
        self.time_manager = TimeManager()
        self.white_draw_requested = False
        self.black_draw_requested = False
        self.last_move = None
        self.position_history = {}  # Hash -> count for threefold repetition detection
        self._record_position()

    def move(self, start, end, player_color, promote_to=None):
        if self.status == GameStatus.COMPLETE:
            return False

        if self.status == GameStatus.IN_PROGRESS:
            current_time = time.time()
            if self.time_manager.check_timeout(self, current_time):
                logging.warning("The player has run out of time")
                return False

        if player_color == self.turn:
            # Regular move - it's the player's turn
            moved = self.board.move(start, end, self.turn, promote_to)
        else:
            # Premove - store for later execution
            if player_color == "white":
                self.white_premove = (start, end, promote_to)
            else:
                self.black_premove = (start, end, promote_to)
            return False

        if moved:
            # Store the last move from the board
            self.last_move = self.board.last_move

            # Reset draw requests when a move is made
            self.reset_draw_requests()

            if self.status == GameStatus.IN_PROGRESS:
                if self.turn == "white":
                    self.white_time_left += MOVE_INCREMENT_IN_SECONDS
                else:
                    self.black_time_left += MOVE_INCREMENT_IN_SECONDS

            if self.status == GameStatus.NOT_STARTED and self.turn == "black":
                self.status = GameStatus.IN_PROGRESS

            self.turn = "black" if self.turn == "white" else "white"
            self.last_move_time = time.time()

            # Record position for threefold repetition detection
            if self._record_position():
                return True  # Game ended due to threefold repetition

            # Execute premove if one exists for the current player
            self._execute_premove()

            if not self.board.can_player_move(self.turn):
                self.status = GameStatus.COMPLETE
                self.completed_at = time.time()
                if self.board.is_king_in_check(self.turn):
                    self.winner = "black" if self.turn == "white" else "white"
                    self.end_reason = "checkmate"
                else:
                    self.winner = "draw"
                    self.end_reason = "stalemate"

            return True  # Move was successfully made
        else:
            return False  # Move was invalid

    def _execute_premove(self):
        """Execute a premove if one exists for the current player"""
        premove = None
        if self.turn == "white" and self.white_premove:
            premove = self.white_premove
            self.white_premove = None
        elif self.turn == "black" and self.black_premove:
            premove = self.black_premove
            self.black_premove = None

        if premove:
            start, end, promote_to = premove
            # Subtract 0.1 seconds for premove penalty only if game hasn't started
            if self.status != GameStatus.NOT_STARTED:
                if self.turn == "white":
                    self.white_time_left = max(
                        0, self.white_time_left - PREMOVE_PENALTY_IN_SECONDS
                    )
                else:
                    self.black_time_left = max(
                        0, self.black_time_left - PREMOVE_PENALTY_IN_SECONDS
                    )
            # Recursively call move with the premove as a regular move
            moved = self.move(start, end, self.turn, promote_to)
            # Update last_move after premove execution
            if moved:
                self.last_move = self.board.last_move

    def _finalize_game_end(self, winner: str, end_reason: str):
        """Helper method to update time and complete the game"""
        if self.status == GameStatus.IN_PROGRESS and end_reason != "time":
            # Only update player time if game is not ending due to timeout
            # (to avoid infinite recursion)
            current_time = time.time()
            self.time_manager.update_player_time(self, current_time)

        self.status = GameStatus.COMPLETE
        self.completed_at = time.time()
        self.winner = winner
        self.end_reason = end_reason

    def mark_player_forfeit(self, color):
        if self.status != GameStatus.COMPLETE:
            winner = "black" if color == "white" else "white"
            self._finalize_game_end(winner, "resignation")

    def request_draw(self, color):
        """Request a draw from the specified player"""
        if self.status not in [GameStatus.IN_PROGRESS]:
            return False

        if color == "white":
            self.white_draw_requested = True
        else:
            self.black_draw_requested = True

        # If both players have requested a draw, end the game in a draw
        if self.white_draw_requested and self.black_draw_requested:
            self._finalize_game_end("draw", "draw_agreement")
            return True

        return False

    def mark_timeout(self, winner: str):
        """Mark the game as complete due to timeout"""
        self._finalize_game_end(winner, "time")

    def reset_draw_requests(self):
        """Reset all draw requests (called when a move is made)"""
        self.white_draw_requested = False
        self.black_draw_requested = False

    def _record_position(self):
        """Record the current board position and check for threefold repetition"""
        position_hash = self.board.get_position_hash(self.turn)
        self.position_history[position_hash] = (
            self.position_history.get(position_hash, 0) + 1
        )

        # Check for threefold repetition
        if self.position_history[position_hash] >= 3:
            self._finalize_game_end("draw", "threefold_repetition")
            return True
        return False

    def is_threefold_repetition(self) -> bool:
        """Check if current position would result in threefold repetition"""
        position_hash = self.board.get_position_hash(self.turn)
        return self.position_history.get(position_hash, 0) >= 2
