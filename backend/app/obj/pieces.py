from .position import Position
from .modifier import Modifier


class Piece:
    PIECE_VALUES = {
        "pawn": 1,
        "knight": 3,
        "bishop": 3,
        "rook": 5,
        "queen": 9,
        "king": 0,
    }

    def __init__(self, color: str, type: str = None, position: Position = None):
        self.color = color
        self.moved = False
        self.type = type
        self.position = position
        self.modifiers: list[Modifier] = []

    def mark_moved(self):
        self.moved = True

    def get_acting_type(self) -> str:
        return self.type

    def get_base_value(self) -> int:
        return self.PIECE_VALUES.get(self.get_acting_type(), 0)

    def add_modifier(self, modifier: Modifier) -> bool:
        if not any(m.modifier_type == modifier.modifier_type for m in self.modifiers):
            self.modifiers.append(modifier)
            return True
        return False

    def remove_modifier(self, modifier_type: str) -> bool:
        for i, modifier in enumerate(self.modifiers):
            if modifier.modifier_type == modifier_type:
                del self.modifiers[i]
                return True
        return False

    def has_modifier(self, modifier_type: str) -> bool:
        return any(m.modifier_type == modifier_type for m in self.modifiers)

    def get_modifier(self, modifier_type: str) -> Modifier:
        for modifier in self.modifiers:
            if modifier.modifier_type == modifier_type:
                return modifier
        return None


class Pawn(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "pawn", position=position)
        self.promoted_to = None  # Track what piece this pawn is acting as

    def promote_to(self, piece_type: str):
        """Promote the pawn to act as the specified piece type"""
        self.promoted_to = piece_type

    def get_acting_type(self) -> str:
        """Get the type this pawn is currently acting as"""
        return self.promoted_to if self.promoted_to else "pawn"


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