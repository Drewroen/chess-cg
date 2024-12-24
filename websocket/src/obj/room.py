from obj.game import Game
import uuid


class Room:
    def __init__(self):
        self.id = uuid.uuid4()
        self.white = None
        self.black = None
        self.game = Game()

    def open(self):
        return self.white is None or self.black is None

    def join(self, player):
        if self.white is None:
            self.white = player
        elif self.black is None:
            self.black = player
        else:
            return False
        return True
