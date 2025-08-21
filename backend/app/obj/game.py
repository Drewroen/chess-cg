from enum import Enum
from app.obj.chess import Board
import time


class GameStatus(Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"
    ABORTED = "aborted"


STARTING_TIME_IN_SECONDS = 180.0
MOVE_INCREMENT_IN_SECONDS = 2.0
PREMOVE_PENALTY_IN_SECONDS = 0.1
GAME_START_TIMEOUT_SECONDS = 10.0


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
        self.white_premove = None
        self.black_premove = None
        self.completed_at = None

    def move(self, start, end, player_color, promote_to=None):
        if self.status == GameStatus.COMPLETE:
            return False

        if self.status == GameStatus.IN_PROGRESS:
            current_time = time.time()
            elapsed = current_time - self.last_move_time
            if self.turn == "white":
                self.white_time_left = round(self.white_time_left - elapsed, 2)
                if self.white_time_left <= 0:
                    print("The player has run out of time")
                    self.white_time_left = 0
                    self.status = GameStatus.COMPLETE
                    self.completed_at = time.time()
                    self.winner = "black"
                    return False
            else:
                self.black_time_left = round(self.black_time_left - elapsed, 2)
                if self.black_time_left <= 0:
                    print("The player has run out of time")
                    self.black_time_left = 0
                    self.status = GameStatus.COMPLETE
                    self.completed_at = time.time()
                    self.winner = "white"
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
            if self.status == GameStatus.IN_PROGRESS:
                if self.turn == "white":
                    self.white_time_left += MOVE_INCREMENT_IN_SECONDS
                else:
                    self.black_time_left += MOVE_INCREMENT_IN_SECONDS

            if self.status == GameStatus.NOT_STARTED and self.turn == "black":
                self.status = GameStatus.IN_PROGRESS

            self.turn = "black" if self.turn == "white" else "white"
            self.last_move_time = time.time()

            # Execute premove if one exists for the current player
            self._execute_premove()

            if not self.board.can_player_move(self.turn):
                self.status = GameStatus.COMPLETE
                self.completed_at = time.time()
                if self.board.is_king_in_check(self.turn):
                    self.winner = "black" if self.turn == "white" else "white"
                else:
                    self.winner = "draw"

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
            self.move(start, end, self.turn, promote_to)

    def mark_player_forfeit(self, color):
        if self.status != GameStatus.COMPLETE:
            # Update the current player's time if game is in progress
            if self.status == GameStatus.IN_PROGRESS:
                current_time = time.time()
                elapsed = current_time - self.last_move_time
                if self.turn == "white":
                    self.white_time_left = max(0, round(self.white_time_left - elapsed, 2))
                else:
                    self.black_time_left = max(0, round(self.black_time_left - elapsed, 2))
            
            self.status = GameStatus.COMPLETE
            self.completed_at = time.time()
            self.winner = "black" if color == "white" else "white"
