class Position:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def notation(self) -> str:
        return f"{chr(self.col + 97)}{8 - self.row}"

    def coordinates(self) -> tuple[int, int]:
        return self.row, self.col

    def to_dict(self) -> dict:
        return {"row": self.row, "col": self.col}


def position_from_notation(notation: str) -> Position:
    col = ord(notation[0].lower()) - 97
    row = 8 - int(notation[1])
    return Position(row, col)


class Piece:
    def __init__(self, color, type=None, position=None):
        self.color = color
        self.moved = False
        self.type = type
        self.position = None

    def mark_moved(self):
        self.moved = True


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "pawn")


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, "rook")


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "knight")


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "bishop")


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, "queen")


class King(Piece):
    def __init__(self, color):
        super().__init__(color, "king")
