import obj.chess as chess
import uuid


class Room:
    def __init__(self):
        self.id = uuid.uuid4()
        self.player1 = None
        self.player2 = None
        self.board = chess.Board()

    def open(self):
        return self.player1 is None or self.player2 is None

    def join(self, player):
        if self.player1 is None:
            self.player1 = player
        elif self.player2 is None:
            self.player2 = player
        else:
            return False
        return True
