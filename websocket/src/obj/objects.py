class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def notation(self):
        return f"{chr(self.col + 97)}{8 - self.row}"

    def to_dict(self):
        return {"row": self.row, "col": self.col}


class Piece:
    def __init__(self, color, type=None):
        self.color = color
        self.moved = False
        self.type = type

    def mark_moved(self):
        self.moved = True
