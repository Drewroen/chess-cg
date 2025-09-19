from typing import List, Optional


class Modifier:
    def __init__(
        self,
        modifier_type: str,
        score: int = 0,
        applicable_pieces: Optional[List[str]] = None,
        description: str = "",
    ):
        self.modifier_type = modifier_type
        self.score = score
        self.applicable_pieces = applicable_pieces or []
        self.description = description

    def can_apply_to_piece(self, piece_type: str) -> bool:
        """Check if this modifier can be applied to the given piece type"""
        if not self.applicable_pieces:
            return True  # No restrictions
        return piece_type in self.applicable_pieces

    def to_dict(self) -> dict:
        return {
            "type": self.modifier_type,
            "score": self.score,
            "applicable_pieces": self.applicable_pieces,
            "description": self.description,
        }


# ROOK MODIFIERS

KNOOK_MODIFIER = Modifier(
    modifier_type="Knook",
    score=4,
    applicable_pieces=["rook"],
    description="A piece that combines the movement of a Knight and a Rook.",
)

DIAGONAL_ROOK_MODIFIER = Modifier(
    modifier_type="DiagonalRook",
    score=2,
    applicable_pieces=["rook"],
    description="A rook that can also move one square diagonally.",
)

QUOOK_MODIFIER = Modifier(
    modifier_type="Quook",
    score=5,
    applicable_pieces=["rook"],
    description="You're the queen of the castle.",
)

BACKWARDS_PAWN_MODIFIER = Modifier(
    modifier_type="BackwardsPawn",
    score=1,
    applicable_pieces=["pawn"],
    description="A pawn that can move one square backward.",
)
