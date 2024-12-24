from obj.chess import Board


class Game:
    def __init__(self):
        self.turn = "white"
        self.board = Board()

    def move(self, start, end):
        moved = self.board.move(start, end)
        if moved:
            self.turn = "black" if self.turn == "white" else "white"
