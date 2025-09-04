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
    def __init__(
        self, color: str, type: str = None, position: Position = None, value: int = 0
    ):
        self.color = color
        self.moved = False
        self.type = type
        self.position = position
        self.value = value

    def mark_moved(self):
        self.moved = True

    def get_acting_type(self) -> str:
        return self.type


class Pawn(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "pawn", position=position, value=1)
        self.promoted_to = None  # Track what piece this pawn is acting as

    def promote_to(self, piece_type: str):
        """Promote the pawn to act as the specified piece type"""
        piece_values = {"queen": 9, "rook": 5, "bishop": 3, "knight": 3}
        self.promoted_to = piece_type
        self.value = piece_values.get(piece_type, 1)

    def get_acting_type(self) -> str:
        """Get the type this pawn is currently acting as"""
        return self.promoted_to if self.promoted_to else "pawn"


class Rook(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "rook", position=position, value=5)


class Knight(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "knight", position=position, value=3)


class Bishop(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "bishop", position=position, value=3)


class Queen(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "queen", position=position, value=9)


class King(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "king", position=position, value=0)
