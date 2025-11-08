class Modifier:
    def __init__(
        self,
        modifier_type: str,
        score: int = 0,
        applicable_piece: str = None,
        description: str = "",
        uses: int = 0,  # Number of times this modifier can be used (0 for unlimited)
    ):
        self.modifier_type = modifier_type
        self.score = score
        self.applicable_piece = applicable_piece
        self.description = description
        self.uses = uses

    def can_apply_to_piece(self, piece_type: str) -> bool:
        """Check if this modifier can be applied to the given piece type"""
        if not self.applicable_piece:
            return True  # No restrictions
        return piece_type == self.applicable_piece

    def to_dict(self) -> dict:
        return {
            "type": self.modifier_type,
            "score": self.score,
            "applicable_piece": self.applicable_piece,
            "description": self.description,
            "uses": self.uses,
        }


# ROOK MODIFIERS

KNOOK_MODIFIER = Modifier(
    modifier_type="Knook",
    score=4,
    applicable_piece="rook",
    description="This piece combines the movement of a Knight and a Rook",
    uses=0,
)

DIAGONAL_ROOK_MODIFIER = Modifier(
    modifier_type="Kitty Castle",
    score=2,
    applicable_piece="rook",
    description="This piece can also move one square diagonally",
    uses=0,
)

QUOOK_MODIFIER = Modifier(
    modifier_type="Quook",
    score=5,
    applicable_piece="rook",
    description="This piece moves like a Queen",
    uses=0,
)

# PAWN MODIFIERS
BACKWARDS_PAWN_MODIFIER = Modifier(
    modifier_type="Reverse",
    score=1,
    applicable_piece="pawn",
    description="This piece can move one square backward",
    uses=0,
)

DIAGONAL_PAWN_MODIFIER = Modifier(
    modifier_type="Kitty",
    score=1,
    applicable_piece="pawn",
    description="This piece can move one square diagonally forward without capturing",
    uses=0,
)

LONG_LEAP_PAWN_MODIFIER = Modifier(
    modifier_type="Long Leaper",
    score=1,
    applicable_piece="pawn",
    description="This piece can move three squares forward on its first move",
    uses=0,
)

# BISHOP MODIFIERS
SIDESTEP_BISHOP_MODIFIER = Modifier(
    modifier_type="Sidestepper",
    score=2,
    applicable_piece="bishop",
    description="This piece can also move one square horizontally",
    uses=0,
)

UNICORN_MODIFIER = Modifier(
    modifier_type="Unicorn",
    score=5,
    applicable_piece="bishop",
    description="This piece combines the movement of a Bishop and a Knight",
    uses=0,
)

CORNER_HOP_MODIFIER = Modifier(
    modifier_type="Corner Hop",
    score=2,
    applicable_piece="bishop",
    description="This piece may move to an open corner",
    uses=1,
)

# KNIGHT MODIFIERS
LONGHORN_MODIFIER = Modifier(
    modifier_type="Longhorn",
    score=3,
    applicable_piece="knight",
    description="This piece can also move two squares in a straight line",
    uses=0,
)
PEGASUS_MODIFIER = Modifier(
    modifier_type="Pegasus",
    score=4,
    applicable_piece="knight",
    description="This piece may also move in an L shape with 2 squares in each direction",
    uses=0,
)
ROYAL_GUARD_MODIFIER = Modifier(
    modifier_type="Royal Guard",
    score=3,
    applicable_piece="knight",
    description="This piece may also move like a king",
    uses=0,
)

# QUEEN MODIFIERS
SACRIFICIAL_QUEEN_MODIFIER = Modifier(
    modifier_type="Sacrificial Lamb",
    score=4,
    applicable_piece="queen",
    description="This piece may move anywhere if the king is in check",
    uses=1,
)

KNEEN_MODIFIER = Modifier(
    modifier_type="Kneen",
    score=4,
    applicable_piece="queen",
    description="This piece combines the movement of a Queen and a Knight",
    uses=0,
)

INFILTRATION_MODIFIER = Modifier(
    modifier_type="Infiltration",
    score=3,
    applicable_piece="queen",
    description="This piece may move to any open space on your opponent's home row",
    uses=1,
)

# KING MODIFIERS
ESCAPE_HATCH_MODIFIER = Modifier(
    modifier_type="Escape Hatch",
    score=3,
    applicable_piece="king",
    description="This piece may move to any unoccupied square on the home row",
    uses=1,
)

AGGRESSIVE_KING_MODIFIER = Modifier(
    modifier_type="Aggression",
    score=4,
    applicable_piece="king",
    description="This piece may move up to two squares in any direction",
    uses=1,
)

TELEPORT_MODIFIER = Modifier(
    modifier_type="Teleport",
    score=4,
    applicable_piece="king",
    description="This piece may swap places with any friendly piece on the board",
    uses=1,
)
