from .position import Position
from .modifier import Modifier
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from .constants import (
    PAWN_DIRECTIONS,
    PAWN_START_ROWS,
    PAWN_PROMOTION_ROWS,
    EN_PASSANT_ROWS,
    KING_MOVES,
    KNIGHT_MOVES,
)

if TYPE_CHECKING:
    from .board import Board
    from .chess_move import ChessMove


class Piece(ABC):
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
        self.modifier_uses_remaining: dict[str, int] = {}

    def mark_moved(self):
        self.moved = True

    def get_acting_type(self) -> str:
        return self.type

    def get_base_value(self) -> int:
        return self.PIECE_VALUES.get(self.get_acting_type(), 0)

    def get_total_value(self) -> int:
        """Get the total value including base value and all modifier scores"""
        base_value = self.get_base_value()
        modifier_score = sum(modifier.score for modifier in self.modifiers)
        return base_value + modifier_score

    def add_modifier(self, modifier: Modifier) -> bool:
        """Add a modifier to this piece if valid and not already present"""
        # Check if modifier can be applied to this piece type
        if not modifier.can_apply_to_piece(self.get_acting_type()):
            return False

        # Check if modifier is already present
        if not any(m.modifier_type == modifier.modifier_type for m in self.modifiers):
            self.modifiers.append(modifier)
            # Initialize remaining uses from the modifier definition
            if modifier.uses > 0:
                self.modifier_uses_remaining[modifier.modifier_type] = modifier.uses
            return True
        return False

    def can_add_modifier(self, modifier: Modifier) -> bool:
        """Check if a modifier can be added to this piece without adding it"""
        return modifier.can_apply_to_piece(self.get_acting_type()) and not any(
            m.modifier_type == modifier.modifier_type for m in self.modifiers
        )

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

    def get_modifier_uses_remaining(self, modifier_type: str) -> int:
        """Get the number of uses remaining for a modifier (0 means unlimited or not present)"""
        return self.modifier_uses_remaining.get(modifier_type, 0)

    def decrement_modifier_uses(self, modifier_type: str) -> bool:
        """Decrement the uses remaining for a modifier. Returns True if successful."""
        if modifier_type in self.modifier_uses_remaining:
            if self.modifier_uses_remaining[modifier_type] > 0:
                self.modifier_uses_remaining[modifier_type] -= 1
                return True
        return False

    @abstractmethod
    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """
        Get all possible moves for this piece on the given board.

        Args:
            board: The board instance containing game state
            ignore_check: If True, include moves that would leave king in check
            ignore_illegal_moves: If True, include technically illegal moves (for analysis)

        Returns:
            List of possible ChessMove objects
        """
        pass


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

    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """Get all possible moves for this pawn"""
        from .chess_move import (
            ChessMove,
        )  # Import at runtime to avoid circular dependency

        row, col = self.position.coordinates()
        color = self.color
        direction = PAWN_DIRECTIONS[color]
        moves = []

        # Forward moves (1 or 2 squares from starting position)
        moves.extend(
            self._get_forward_moves(
                board, row, col, color, direction, ignore_illegal_moves
            )
        )

        # Diagonal captures (including promotions)
        moves.extend(
            self._get_capture_moves(
                board, row, col, color, direction, ignore_illegal_moves
            )
        )

        # En passant captures
        moves.extend(
            self._get_en_passant_moves(
                board, row, col, color, direction, ignore_illegal_moves
            )
        )

        if self.has_modifier("Reverse"):
            moves.extend(
                self._get_backward_moves(
                    board, row, col, color, direction, ignore_illegal_moves
                )
            )

        return moves

    def _get_forward_moves(
        self,
        board: "Board",
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool,
    ) -> List["ChessMove"]:
        """Get forward moves for a pawn (1 or 2 squares)"""
        from .chess_move import ChessMove

        moves = []
        target_row = row + direction

        # Check if one square forward is valid and empty
        if not (
            board.is_valid_position(target_row, col)
            and (board.is_empty_square(target_row, col) or ignore_illegal_moves)
        ):
            return moves

        # Handle promotion or regular move
        if target_row == PAWN_PROMOTION_ROWS[color]:
            moves.extend(
                board.create_promotion_moves(self.position, target_row, col, color)
            )
        else:
            moves.append(ChessMove(self.position, Position(target_row, col)))

            # Check for two-square initial move
            if (
                row == PAWN_START_ROWS[color]
                and board.is_valid_position(target_row + direction, col)
                and (
                    board.is_empty_square(target_row + direction, col)
                    or ignore_illegal_moves
                )
            ):
                moves.append(
                    ChessMove(self.position, Position(target_row + direction, col))
                )

            if self.has_modifier("Long Leaper"):
                # Check for three-square initial move
                if (
                    row == PAWN_START_ROWS[color]
                    and board.is_valid_position(target_row + (2 * direction), col)
                    and (
                        board.is_empty_square(target_row + (2 * direction), col)
                        or ignore_illegal_moves
                    )
                ):
                    moves.append(
                        ChessMove(
                            self.position, Position(target_row + (2 * direction), col)
                        )
                    )

        return moves

    def _get_backward_moves(
        self,
        board: "Board",
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool,
    ) -> List["ChessMove"]:
        """Get backward moves for a pawn if it has the Reverse modifier"""

        moves = []

        target_row = row - direction

        # Check if one square backward is valid and empty
        if board.is_valid_position(target_row, col) and (
            board.is_empty_square(target_row, col) or ignore_illegal_moves
        ):
            moves.append(ChessMove(self.position, Position(target_row, col)))

        return moves

    def _get_capture_moves(
        self,
        board: "Board",
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool,
    ) -> List["ChessMove"]:
        """Get diagonal capture moves for a pawn"""
        from .chess_move import ChessMove

        moves = []
        target_row = row + direction

        # Check both diagonal directions
        for col_offset in [-1, 1]:
            target_col = col + col_offset

            if not board.is_valid_position(target_row, target_col):
                continue

            if not board.is_enemy_piece(target_row, target_col, color):
                if not self.has_modifier("Kitty"):
                    continue

            # Handle promotion or regular capture
            if target_row == PAWN_PROMOTION_ROWS[color]:
                moves.extend(
                    board.create_promotion_moves(
                        self.position, target_row, target_col, color
                    )
                )
            else:
                moves.append(ChessMove(self.position, Position(target_row, target_col)))

        return moves

    def _get_en_passant_moves(
        self,
        board: "Board",
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool,
    ) -> List["ChessMove"]:
        """Get en passant moves for a pawn"""
        from .chess_move import ChessMove

        moves = []

        # En passant is only possible from specific rows
        if row != EN_PASSANT_ROWS[color]:
            return moves

        # Check both sides for en passant opportunities
        for col_offset in [-1, 1]:
            target_col = col + col_offset

            if board.is_valid_position(row, target_col) and (
                board.can_capture_en_passant(row, target_col, color)
                or ignore_illegal_moves
            ):
                capture_position = Position(row, target_col)
                move_position = Position(row + direction, target_col)
                moves.append(ChessMove(self.position, move_position, capture_position))

        return moves


class Rook(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "rook", position=position)

    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """Get all possible moves for this rook"""
        # Rook moves horizontally and vertically
        rook_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        bishop_directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

        if self.has_modifier("Quook"):
            return board.get_sliding_moves(
                self.position, rook_directions + bishop_directions, ignore_illegal_moves
            )

        moves = board.get_sliding_moves(
            self.position, rook_directions, ignore_illegal_moves
        )

        if self.has_modifier("Knook"):
            moves.extend(
                board.get_knight_moves(self.position, self.color, ignore_illegal_moves)
            )

        if self.has_modifier("Kitty Castle"):
            moves.extend(
                board.get_sliding_moves(
                    self.position,
                    bishop_directions,
                    ignore_illegal_moves,
                    1,
                )
            )
        return moves


class Knight(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "knight", position=position)

    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """Get all possible moves for this knight"""
        from .chess_move import ChessMove

        moves = board.get_knight_moves(self.position, self.color, ignore_illegal_moves)

        # Longhorn modifier: can also move two squares in a straight line
        if self.has_modifier("Longhorn"):
            row, col = self.position.coordinates()
            # Straight-line two-square moves (up, down, left, right)
            straight_moves = [(2, 0), (-2, 0), (0, 2), (0, -2)]

            for dr, dc in straight_moves:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    target_piece = board.squares[new_row][new_col]
                    if ignore_illegal_moves or (
                        target_piece is None or target_piece.color != self.color
                    ):
                        moves.append(
                            ChessMove(self.position, Position(new_row, new_col))
                        )

        # Pegasus modifier: can also move in an L-shape with 2 squares in each direction
        if self.has_modifier("Pegasus"):
            row, col = self.position.coordinates()
            # Extended L-shaped moves (2x2 instead of 2x1)
            pegasus_moves = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

            for dr, dc in pegasus_moves:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    target_piece = board.squares[new_row][new_col]
                    if ignore_illegal_moves or (
                        target_piece is None or target_piece.color != self.color
                    ):
                        moves.append(
                            ChessMove(self.position, Position(new_row, new_col))
                        )

        # Royal Guard modifier: can also move like a king
        if self.has_modifier("Royal Guard"):
            row, col = self.position.coordinates()
            # Add king moves (one square in any direction)
            for dr, dc in KING_MOVES:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    target_piece = board.squares[new_row][new_col]
                    if ignore_illegal_moves or (
                        target_piece is None or target_piece.color != self.color
                    ):
                        moves.append(
                            ChessMove(self.position, Position(new_row, new_col))
                        )

        return moves


class Bishop(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "bishop", position=position)

    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """Get all possible moves for this bishop"""
        # Bishop moves diagonally
        directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        moves = board.get_sliding_moves(self.position, directions, ignore_illegal_moves)

        if self.has_modifier("Sidestepper"):
            # Add horizontal one-square moves
            horizontal_directions = [(0, 1), (0, -1)]
            moves.extend(
                board.get_sliding_moves(
                    self.position,
                    horizontal_directions,
                    ignore_illegal_moves,
                    1,
                )
            )

        if self.has_modifier("Unicorn"):
            # Add knight moves
            moves.extend(
                board.get_knight_moves(self.position, self.color, ignore_illegal_moves)
            )

        if (
            self.has_modifier("Corner Hop")
            and self.get_modifier_uses_remaining("Corner Hop") > 0
        ):
            # Add moves to any open corner square
            corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
            for corner_row, corner_col in corners:
                if (
                    board.is_empty_square(corner_row, corner_col)
                    or ignore_illegal_moves
                ):
                    corner_pos = Position(corner_row, corner_col)
                    move = ChessMove(self.position, corner_pos)
                    move.used_modifier = "Corner Hop"
                    moves.append(move)

        return moves


class Queen(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "queen", position=position)

    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """Get all possible moves for this queen"""
        from .chess_move import ChessMove

        # Queen combines rook and bishop moves (horizontal, vertical, and diagonal)
        rook_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        bishop_directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        all_directions = rook_directions + bishop_directions
        moves = board.get_sliding_moves(
            self.position, all_directions, ignore_illegal_moves
        )

        # Kneen: can also move like a knight
        if self.has_modifier("Kneen"):
            moves.extend(
                board.get_knight_moves(self.position, self.color, ignore_illegal_moves)
            )

        # Sacrificial Lamb: can move to any square if king is in check
        if (
            self.has_modifier("Sacrificial Lamb")
            and self.get_modifier_uses_remaining("Sacrificial Lamb") > 0
            and board.is_king_in_check(self.color)
        ):
            # Add moves to every square on the board
            for row in range(8):
                for col in range(8):
                    target_piece = board.squares[row][col]
                    # Can move to empty squares or capture enemy pieces
                    if ignore_illegal_moves or (
                        target_piece is None or target_piece.color != self.color
                    ):
                        target_pos = Position(row, col)
                        # Skip if this is the queen's current position
                        if target_pos.coordinates() != self.position.coordinates():
                            move = ChessMove(self.position, target_pos)
                            move.used_modifier = "Sacrificial Lamb"
                            moves.append(move)

        # Infiltration: can move to any open space on opponent's home row
        if (
            self.has_modifier("Infiltration")
            and self.get_modifier_uses_remaining("Infiltration") > 0
        ):
            # Determine opponent's home row (row 0 for white, row 7 for black)
            opponent_home_row = 0 if self.color == "black" else 7

            # Add moves to all empty squares on opponent's home row
            for col in range(8):
                target_piece = board.squares[opponent_home_row][col]
                # Can only move to empty squares
                if ignore_illegal_moves or target_piece is None:
                    target_pos = Position(opponent_home_row, col)
                    # Skip if this is the queen's current position
                    if target_pos.coordinates() != self.position.coordinates():
                        move = ChessMove(self.position, target_pos)
                        move.used_modifier = "Infiltration"
                        moves.append(move)

        return moves


class King(Piece):
    def __init__(self, color, position: Position = None):
        super().__init__(color, "king", position=position)

    def get_possible_moves(
        self,
        board: "Board",
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> List["ChessMove"]:
        """Get all possible moves for this king"""
        from .chess_move import ChessMove

        moves = []
        row, col = self.position.coordinates()

        # Standard king moves
        for dr, dc in KING_MOVES:
            new_row, new_col = row + dr, col + dc
            if board.is_valid_position(new_row, new_col):
                target_piece = board.squares[new_row][new_col]
                if ignore_illegal_moves or (
                    target_piece is None or target_piece.color != self.color
                ):
                    moves.append(ChessMove(self.position, Position(new_row, new_col)))

        # Castling logic
        if (not ignore_check or ignore_illegal_moves) and not self.moved:
            moves.extend(self._get_castling_moves(board, ignore_illegal_moves))

        # Aggression: can move to any square within 2-square radius
        if (
            self.has_modifier("Aggression")
            and self.get_modifier_uses_remaining("Aggression") > 0
        ):
            # Add moves for 2-square radius in all 8 directions
            for dr, dc in KING_MOVES:
                # Move 2 squares in this direction
                new_row, new_col = row + (dr * 2), col + (dc * 2)
                if board.is_valid_position(new_row, new_col):
                    target_piece = board.squares[new_row][new_col]
                    if ignore_illegal_moves or (
                        target_piece is None or target_piece.color != self.color
                    ):
                        move = ChessMove(self.position, Position(new_row, new_col))
                        move.used_modifier = "Aggression"
                        moves.append(move)

            # Also add knight moves (covers remaining squares in 2-square radius)
            moves.append(
                board.get_knight_moves(self.position, self.color, ignore_illegal_moves)
            )

        # Escape Hatch: can move to any unoccupied square on the home row
        if (
            self.has_modifier("Escape Hatch")
            and self.get_modifier_uses_remaining("Escape Hatch") > 0
        ):
            # Determine king's home row (row 0 for white, row 7 for black)
            home_row = 0 if self.color == "white" else 7

            # Add moves to all empty squares on home row
            for col in range(8):
                target_piece = board.squares[home_row][col]
                # Can only move to empty squares
                if ignore_illegal_moves or target_piece is None:
                    target_pos = Position(home_row, col)
                    # Skip if this is the king's current position
                    if target_pos.coordinates() != self.position.coordinates():
                        move = ChessMove(self.position, target_pos)
                        move.used_modifier = "Escape Hatch"
                        moves.append(move)

        # Teleport: can swap places with any friendly piece
        if (
            self.has_modifier("Teleport")
            and self.get_modifier_uses_remaining("Teleport") > 0
        ):
            # Add moves to swap with every friendly piece on the board
            for row in range(8):
                for col in range(8):
                    target_piece = board.squares[row][col]
                    # Can only swap with friendly pieces
                    if target_piece is not None and target_piece.color == self.color:
                        target_pos = Position(row, col)
                        # Skip if this is the king's current position
                        if target_pos.coordinates() != self.position.coordinates():
                            move = ChessMove(self.position, target_pos)
                            # The additional_move swaps the friendly piece to king's position
                            move.additional_move = (target_pos, self.position)
                            move.used_modifier = "Teleport"
                            moves.append(move)

        return moves

    def _get_castling_moves(
        self, board: "Board", ignore_illegal_moves: bool = False
    ) -> List["ChessMove"]:
        """Get castling moves for this king"""
        from .chess_move import ChessMove

        moves = []
        row, col = self.position.coordinates()

        # Kingside castling
        if board.can_castle_kingside(row, col, self.color) or ignore_illegal_moves:
            move = ChessMove(self.position, Position(row, col + 2))
            move.additional_move = (Position(row, col + 3), Position(row, col + 1))
            moves.append(move)

        # Queenside castling
        if board.can_castle_queenside(row, col, self.color) or ignore_illegal_moves:
            move = ChessMove(self.position, Position(row, col - 2))
            move.additional_move = (Position(row, col - 4), Position(row, col - 1))
            moves.append(move)

        return moves
