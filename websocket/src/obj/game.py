from enum import Enum
from obj.chess import Board


class GameStatus(Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"


class Game:
    def __init__(self):
        self.turn = "white"
        self.board = Board()
        self.status = GameStatus.NOT_STARTED  # Use GameStatus enum

    def move(self, start, end):
        if self.status == GameStatus.COMPLETE:
            return
        if self.status == GameStatus.NOT_STARTED and self.turn == "black":
            self.status = GameStatus.IN_PROGRESS
        moved = self.board.move(start, end, self.turn)
        if moved:
            self.turn = "black" if self.turn == "white" else "white"
            if not self.board.can_player_move(self.turn):
                self.status = GameStatus.COMPLETE
