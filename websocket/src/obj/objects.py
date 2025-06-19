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
    def __init__(self, color: str, type: str = None, position: Position = None):
        self.color = color
        self.moved = False
        self.type = type
        self.position = position

    def mark_moved(self):
        self.moved = True


class Pawn(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "pawn", position=position)


class Rook(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "rook", position=position)


class Knight(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "knight", position=position)


class Bishop(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "bishop", position=position)


class Queen(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "queen", position=position)


class King(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "king", position=position)
