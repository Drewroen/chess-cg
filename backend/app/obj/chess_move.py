from app.obj.pieces import Position


class ChessMove:
    def __init__(
        self,
        position_from: Position,
        position_to: Position,
        position_to_capture: Position = None,
        promote_to_type: str = None,
        promote_from_type: str = None,
        additional_move: tuple[Position, Position] = None,
        used_modifier: str = None,
    ):
        self.position_from = position_from
        self.position_to = position_to
        self.position_to_capture = (
            position_to_capture if position_to_capture else position_to
        )
        self.promote_to_type = promote_to_type  # For pawn promotion
        self.promote_from_type = (
            promote_from_type  # Original piece type before promotion
        )
        self.additional_move = additional_move
        self.used_modifier = used_modifier  # Track which modifier enabled this move

    def to_dict(self):
        return {
            "from": self.position_from.to_dict(),
            "to": self.position_to.to_dict(),
        }