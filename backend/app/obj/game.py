from enum import Enum
from app.obj.chess import Board
import time


class GameStatus(Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"


class Game:
    def __init__(self):
        self.turn = "white"
        self.board = Board()
        self.status = GameStatus.NOT_STARTED
        self.white_time_left = 300.0
        self.black_time_left = 300.0
        self.last_move_time = time.time()
        self.winner = None

    def move(self, start, end, promote_to=None):
        if self.status == GameStatus.COMPLETE:
            return

        if self.status == GameStatus.IN_PROGRESS:
            current_time = time.time()
            elapsed = current_time - self.last_move_time
            if self.turn == "white":
                self.white_time_left = round(self.white_time_left - elapsed, 2)
            else:
                self.black_time_left = round(self.black_time_left - elapsed, 2)

        moved = self.board.move(start, end, self.turn, promote_to)
        if moved:
            if self.status == GameStatus.IN_PROGRESS:
                if self.turn == "white":
                    self.white_time_left += 3
                else:
                    self.black_time_left += 3

            if self.status == GameStatus.NOT_STARTED and self.turn == "black":
                self.status = GameStatus.IN_PROGRESS

            self.turn = "black" if self.turn == "white" else "white"
            self.last_move_time = time.time()

            if not self.board.can_player_move(self.turn):
                self.status = GameStatus.COMPLETE
                if self.board.is_king_in_check(self.turn):
                    self.winner = "black" if self.turn == "white" else "white"
                else:
                    self.winner = "draw"

    def mark_player_forfeit(self, color):
        if self.status != GameStatus.COMPLETE:
            self.status = GameStatus.COMPLETE
            self.winner = "black" if color == "white" else "white"
