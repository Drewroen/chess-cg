from obj.objects import Piece, Position


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


class ChessMove:
    def __init__(
        self,
        position_from: Position,
        position_to: Position,
        position_to_capture: Position = None,
        transform_to: Piece = None,
        additional_move: tuple[Position, Position] = None,
    ):
        self.position_from = position_from
        self.position_to = position_to
        self.position_to_capture = (
            position_to_capture if position_to_capture else position_to
        )
        self.transform_to = transform_to  # For pawn promotion
        self.additional_move = additional_move

    def to_dict(self):
        return {
            "position_to_move": self.position_to.to_dict(),
            "position_to_capture": self.position_to_capture.to_dict(),
        }


class Board:
    def __init__(self):
        self.squares: list[list[Piece]] = [[None] * 8 for _ in range(8)]
        self.last_move: ChessMove = None
        self.initialize_board()

    def get_squares(self):
        return [
            [
                {"type": piece.type, "color": piece.color} if piece else None
                for piece in row
            ]
            for row in self.squares
        ]

    def kings_in_check(self) -> dict[str, bool]:
        """
        Check if each king is in check.
        Returns a dictionary with keys 'white' and 'black', where the value is True if the king is in check.
        """
        king_positions = {"white": None, "black": None}
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.type == "king":
                    king_positions[piece.color] = Position(row, col)

        in_check = {"white": False, "black": False}
        for color, king_pos in king_positions.items():
            if king_pos and self._is_square_attacked(king_pos, color):
                in_check[color] = True
        return in_check

    def move(
        self,
        position_from: Position,
        position_to: Position,
        turn: str,
        promote_to: str = None,
    ):
        """
        Move a piece from the first position to the second position
        Returns True if the move was successful, False otherwise
        """
        piece = self.piece_from_position(position_from)
        if piece is None or piece.color != turn:
            return False  # Invalid move if no piece or wrong color's turn

        first_position = position_from.notation()
        second_position = position_to.notation()
        available_moves: list[ChessMove] = self.get_available_moves(position_from)
        move: ChessMove = next(
            filter(
                lambda move: move.position_to.notation() == second_position
                and (
                    (move.transform_to is None and promote_to is None)
                    or move.transform_to.type == promote_to
                ),
                available_moves,
            ),
            None,
        )

        if move:
            initial_position = position_from.coordinates()
            position_to = move.position_to.coordinates()
            position_to_capture = move.position_to_capture.coordinates()

            piece = self.piece_from_position(position_from)
            self.squares[position_to_capture[0]][position_to_capture[1]] = None
            self.squares[position_to[0]][position_to[1]] = move.transform_to or piece
            self.squares[initial_position[0]][initial_position[1]] = None
            piece.mark_moved()
            self.last_move = (first_position, second_position)

            if move.additional_move:
                additional_piece = self.piece_from_position(move.additional_move[0])
                if additional_piece:
                    # Move the additional piece (like in castling)
                    additional_initial_position = move.additional_move[0].coordinates()
                    additional_position_to = move.additional_move[1].coordinates()
                    self.squares[additional_position_to[0]][
                        additional_position_to[1]
                    ] = additional_piece
                    self.squares[additional_initial_position[0]][
                        additional_initial_position[1]
                    ] = None
                    additional_piece.mark_moved()

            return True

        return False

    def get_available_moves(
        self, position: Position, ignore_check: bool = False
    ) -> list[ChessMove]:
        """
        Get the available moves for a piece in the given position
        """
        piece = self.piece_from_position(position)
        if piece is None:
            return []
        moves = []
        if piece.type == "pawn":
            moves = self._get_pawn_moves(position)
        if piece.type == "rook":
            moves = self._get_rook_moves(position)
        if piece.type == "knight":
            moves = self._get_knight_moves(position)
        if piece.type == "bishop":
            moves = self._get_bishop_moves(position)
        if piece.type == "queen":
            moves = self._get_rook_moves(position) + self._get_bishop_moves(position)
        if piece.type == "king":
            moves = self._get_king_moves(position, ignore_check)

        if not ignore_check:
            moves = [
                m for m in moves if not self._is_king_in_check_after_move(position, m)
            ]

        return moves

    def _is_king_in_check_after_move(self, position: Position, move: ChessMove) -> bool:
        """
        Check if the king would be in check after making the given move
        """
        # Simulate the move
        initial_position = position.coordinates()
        target_position = move.position_to.coordinates()
        captured_position = move.position_to_capture.coordinates()

        original_piece = self.piece_from_position(position)
        captured_piece = self.squares[captured_position[0]][captured_position[1]]

        # Temporarily make the move
        temp_piece = self.squares[target_position[0]][target_position[1]]
        self.squares[initial_position[0]][initial_position[1]] = None
        self.squares[captured_position[0]][captured_position[1]] = None
        self.squares[target_position[0]][target_position[1]] = (
            move.transform_to if move.transform_to else original_piece
        )

        # Find the king's position
        king_position = None
        for row in range(8):
            for col in range(8):
                if (
                    self.squares[row][col]
                    and self.squares[row][col].type == "king"
                    and self.squares[row][col].color == original_piece.color
                ):
                    king_position = Position(row, col)
                    break
            if king_position:
                break

        # Check if the king is in check
        in_check = self._is_square_attacked(king_position, original_piece.color)

        # Undo the move
        self.squares[initial_position[0]][initial_position[1]] = original_piece
        self.squares[captured_position[0]][captured_position[1]] = captured_piece
        self.squares[target_position[0]][target_position[1]] = temp_piece

        return in_check

    def _is_square_attacked(self, position: Position, color: str) -> bool:
        """
        Check if a square is attacked by any piece of the opposite color
        """
        row, col = position.coordinates()
        for r in range(8):
            for c in range(8):
                piece = self.squares[r][c]
                if piece and piece.color != color:
                    moves = self.get_available_moves(Position(r, c), ignore_check=True)
                    for move in moves:
                        if move.position_to.coordinates() == (row, col):
                            return True
        return False

    def chess_notation_from_index(self, row: int, col: int):
        return f"{chr(97+col)}{8-row}"

    def _get_pawn_moves(self, position: Position) -> list[ChessMove]:
        """
        Get the available moves for a pawn in the given position
        """
        piece = self.piece_from_position(position)
        moves = []
        row, col = position.coordinates()

        # Check moves for white pawns
        if piece.color == "white":
            # If the pawn is in its initial position, it can move two squares forward
            if row == 6:
                if self.squares[4][col] is None and self.squares[5][col] is None:
                    moves.append(ChessMove(position, Position(4, col)))
            # Move one square forward if the square is empty
            if self.squares[row - 1][col] is None:
                if row != 1:
                    moves.append(ChessMove(position, Position(row - 1, col)))
                else:
                    for piece in [
                        Bishop("white"),
                        Knight("white"),
                        Rook("white"),
                        Queen("white"),
                    ]:
                        moves.append(
                            ChessMove(
                                position, Position(row - 1, col), transform_to=piece
                            )
                        )
            # Capture diagonally
            if (
                col - 1 >= 0
                and self.squares[row - 1][col - 1] is not None
                and self.squares[row - 1][col - 1].color != piece.color
            ):
                if row != 1:
                    moves.append(ChessMove(position, Position(row - 1, col - 1)))
                else:
                    for piece in [
                        Bishop("white"),
                        Knight("white"),
                        Rook("white"),
                        Queen("white"),
                    ]:
                        moves.append(
                            ChessMove(
                                position, Position(row - 1, col - 1), transform_to=piece
                            )
                        )
            if (
                col + 1 < 8
                and self.squares[row - 1][col + 1] is not None
                and self.squares[row - 1][col + 1].color != piece.color
            ):
                if row != 1:
                    moves.append(ChessMove(position, Position(row - 1, col + 1)))
                else:
                    for piece in [
                        Bishop("white"),
                        Knight("white"),
                        Rook("white"),
                        Queen("white"),
                    ]:
                        moves.append(
                            ChessMove(
                                position, Position(row - 1, col + 1), transform_to=piece
                            )
                        )
            # En passant
            if row == 3:
                if (
                    col - 1 >= 0
                    and self.squares[row][col - 1] is not None
                    and self.squares[row][col - 1].type == "pawn"
                    and self.squares[row][col - 1].color != piece.color
                    and self.last_move
                    == (
                        self.chess_notation_from_index(row - 2, col - 1),
                        self.chess_notation_from_index(row, col - 1),
                    )
                ):
                    moves.append(
                        ChessMove(
                            position,
                            Position(row - 1, col - 1),
                            Position(row, col - 1),
                        )
                    )
                if (
                    col + 1 < 8
                    and self.squares[row][col + 1] is not None
                    and self.squares[row][col + 1].type == "pawn"
                    and self.squares[row][col + 1].color != piece.color
                    and self.last_move
                    == (
                        self.chess_notation_from_index(row - 2, col + 1),
                        self.chess_notation_from_index(row, col + 1),
                    )
                ):
                    moves.append(
                        ChessMove(
                            position,
                            Position(row - 1, col + 1),
                            Position(row, col + 1),
                        )
                    )

        else:
            # Check moves for black pawns
            # If the pawn is in its initial position, it can move two squares forward
            if row == 1:
                if self.squares[3][col] is None and self.squares[2][col] is None:
                    moves.append(ChessMove(position, Position(3, col)))
            # Move one square forward if the square is empty
            if self.squares[row + 1][col] is None:
                if row != 6:
                    moves.append(ChessMove(position, Position(row + 1, col)))
                else:
                    for piece in [
                        Bishop("black"),
                        Knight("black"),
                        Rook("black"),
                        Queen("black"),
                    ]:
                        moves.append(
                            ChessMove(
                                position, Position(row + 1, col), transform_to=piece
                            )
                        )
            # Capture diagonally
            if (
                col - 1 >= 0
                and self.squares[row + 1][col - 1] is not None
                and self.squares[row + 1][col - 1].color != piece.color
            ):
                if row != 6:
                    moves.append(ChessMove(position, Position(row + 1, col - 1)))
                else:
                    for piece in [
                        Bishop("black"),
                        Knight("black"),
                        Rook("black"),
                        Queen("black"),
                    ]:
                        moves.append(
                            ChessMove(
                                position, Position(row + 1, col - 1), transform_to=piece
                            )
                        )
            if (
                col + 1 < 8
                and self.squares[row + 1][col + 1] is not None
                and self.squares[row + 1][col + 1].color != piece.color
            ):
                if row != 6:
                    moves.append(ChessMove(position, Position(row + 1, col + 1)))
                else:
                    for piece in [
                        Bishop("black"),
                        Knight("black"),
                        Rook("black"),
                        Queen("black"),
                    ]:
                        moves.append(
                            ChessMove(
                                position, Position(row + 1, col + 1), transform_to=piece
                            )
                        )
            # En passant
            if row == 4:
                if (
                    col - 1 >= 0
                    and self.squares[row][col - 1] is not None
                    and self.squares[row][col - 1].type == "pawn"
                    and self.squares[row][col - 1].color != piece.color
                    and self.last_move
                    == (
                        self.chess_notation_from_index(row + 2, col - 1),
                        self.chess_notation_from_index(row, col - 1),
                    )
                ):
                    moves.append(
                        ChessMove(
                            position,
                            Position(row + 1, col - 1),
                            Position(row, col - 1),
                        )
                    )
                if (
                    col + 1 < 8
                    and self.squares[row][col + 1] is not None
                    and self.squares[row][col + 1].type == "pawn"
                    and self.squares[row][col + 1].color != piece.color
                    and self.last_move
                    == (
                        self.chess_notation_from_index(row + 2, col + 1),
                        self.chess_notation_from_index(row, col + 1),
                    )
                ):
                    moves.append(
                        ChessMove(
                            position,
                            Position(row + 1, col + 1),
                            Position(row, col + 1),
                        )
                    )

        return moves

    def _get_rook_moves(self, position: Position) -> list[ChessMove]:
        """
        Get the available moves for a rook in the given position
        """
        moves = []
        row, col = position.coordinates()

        # Check moves to the right
        for i in range(col + 1, 8):
            if self.squares[row][i] is None:
                moves.append(ChessMove(position, Position(row, i)))
            else:
                if self.squares[row][i].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(row, i)))
                break

        # Check moves to the left
        for i in range(col - 1, -1, -1):
            if self.squares[row][i] is None:
                moves.append(ChessMove(position, Position(row, i)))
            else:
                if self.squares[row][i].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(row, i)))
                break

        # Check moves upwards
        for i in range(row - 1, -1, -1):
            if self.squares[i][col] is None:
                moves.append(ChessMove(position, Position(i, col)))
            else:
                if self.squares[i][col].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(i, col)))
                break

        # Check moves downwards
        for i in range(row + 1, 8):
            if self.squares[i][col] is None:
                moves.append(ChessMove(position, Position(i, col)))
            else:
                if self.squares[i][col].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(i, col)))
                break

        return moves

    def _get_knight_moves(self, position: Position) -> list[ChessMove]:
        """
        Get the available moves for a knight in the given position
        """
        moves = []
        row, col = position.coordinates()

        # Check moves in the first quadrant
        if row - 2 >= 0 and col + 1 < 8:
            if (
                self.squares[row - 2][col + 1] is None
                or self.squares[row - 2][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 2, col + 1)))
        if row - 1 >= 0 and col + 2 < 8:
            if (
                self.squares[row - 1][col + 2] is None
                or self.squares[row - 1][col + 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 1, col + 2)))

        # Check moves in the second quadrant
        if row - 2 >= 0 and col - 1 >= 0:
            if (
                self.squares[row - 2][col - 1] is None
                or self.squares[row - 2][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 2, col - 1)))
        if row - 1 >= 0 and col - 2 >= 0:
            if (
                self.squares[row - 1][col - 2] is None
                or self.squares[row - 1][col - 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 1, col - 2)))

        # Check moves in the third quadrant
        if row + 1 < 8 and col - 2 >= 0:
            if (
                self.squares[row + 1][col - 2] is None
                or self.squares[row + 1][col - 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 1, col - 2)))
        if row + 2 < 8 and col - 1 >= 0:
            if (
                self.squares[row + 2][col - 1] is None
                or self.squares[row + 2][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 2, col - 1)))

        # Check moves in the fourth quadrant
        if row + 1 < 8 and col + 2 < 8:
            if (
                self.squares[row + 1][col + 2] is None
                or self.squares[row + 1][col + 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 1, col + 2)))
        if row + 2 < 8 and col + 1 < 8:
            if (
                self.squares[row + 2][col + 1] is None
                or self.squares[row + 2][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 2, col + 1)))

        return moves

    def _get_bishop_moves(self, position: Position) -> list[ChessMove]:
        """
        Get the available moves for a bishop in the given position
        """
        moves = []
        row, col = position.coordinates()

        # Check moves in the first quadrant
        for i in range(1, min(8 - row, 8 - col)):
            if self.squares[row + i][col + i] is None:
                moves.append(ChessMove(position, Position(row + i, col + i)))
            else:
                if self.squares[row + i][col + i].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(row + i, col + i)))
                break

        # Check moves in the second quadrant
        for i in range(1, min(8 - row, col + 1)):
            if self.squares[row + i][col - i] is None:
                moves.append(ChessMove(position, Position(row + i, col - i)))
            else:
                if self.squares[row + i][col - i].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(row + i, col - i)))
                break

        # Check moves in the third quadrant
        for i in range(1, min(row + 1, col + 1)):
            if self.squares[row - i][col - i] is None:
                moves.append(ChessMove(position, Position(row - i, col - i)))
            else:
                if self.squares[row - i][col - i].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(row - i, col - i)))
                break

        # Check moves in the fourth quadrant
        for i in range(1, min(row + 1, 8 - col)):
            if self.squares[row - i][col + i] is None:
                moves.append(ChessMove(position, Position(row - i, col + i)))
            else:
                if self.squares[row - i][col + i].color != self.squares[row][col].color:
                    moves.append(ChessMove(position, Position(row - i, col + i)))
                break

        return moves

    def _get_king_moves(
        self, position: Position, ignore_check: bool = False
    ) -> list[ChessMove]:
        """
        Get the available moves for a king in the given position, including castling
        """
        moves = []
        row, col = position.coordinates()

        # Check standard king moves
        # Check moves in the first quadrant
        if row - 1 >= 0 and col + 1 < 8:
            if (
                self.squares[row - 1][col + 1] is None
                or self.squares[row - 1][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 1, col + 1)))
        if row - 1 >= 0:
            if (
                self.squares[row - 1][col] is None
                or self.squares[row - 1][col].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 1, col)))

        # Check moves in the second quadrant
        if row - 1 >= 0 and col - 1 >= 0:
            if (
                self.squares[row - 1][col - 1] is None
                or self.squares[row - 1][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row - 1, col - 1)))
        if col - 1 >= 0:
            if (
                self.squares[row][col - 1] is None
                or self.squares[row][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row, col - 1)))

        # Check moves in the third quadrant
        if row + 1 < 8 and col - 1 >= 0:
            if (
                self.squares[row + 1][col - 1] is None
                or self.squares[row + 1][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 1, col - 1)))
        if row + 1 < 8:
            if (
                self.squares[row + 1][col] is None
                or self.squares[row + 1][col].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 1, col)))

        # Check moves in the fourth quadrant
        if row + 1 < 8 and col + 1 < 8:
            if (
                self.squares[row + 1][col + 1] is None
                or self.squares[row + 1][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row + 1, col + 1)))
        if col + 1 < 8:
            if (
                self.squares[row][col + 1] is None
                or self.squares[row][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(position, Position(row, col + 1)))

        color = self.squares[row][col].color
        # Castling: only when not ignoring checks
        if not ignore_check and not self.squares[row][col].moved:
            # kingside
            if (
                col + 2 < 8
                and self.squares[row][col + 1] is None
                and self.squares[row][col + 2] is None
                and isinstance(self.squares[row][col + 3], Rook)
                and not self.squares[row][col + 3].moved
            ):
                safe = True
                if not ignore_check:
                    if self._is_square_attacked(position, color):
                        safe = False
                    if self._is_square_attacked(Position(row, col + 1), color):
                        safe = False
                    if self._is_square_attacked(Position(row, col + 2), color):
                        safe = False
                if safe:
                    move = ChessMove(position, Position(row, col + 2))
                    move.additional_move = (
                        Position(row, col + 3),
                        Position(row, col + 1),
                    )
                    moves.append(move)
            # queenside
            if (
                col - 2 >= 0
                and self.squares[row][col - 1] is None
                and self.squares[row][col - 2] is None
                and self.squares[row][col - 3] is None
                and isinstance(self.squares[row][col - 4], Rook)
                and not self.squares[row][col - 4].moved
            ):
                safe = True
                if not ignore_check:
                    if self._is_square_attacked(position, color):
                        safe = False
                    if self._is_square_attacked(Position(row, col - 1), color):
                        safe = False
                    if self._is_square_attacked(Position(row, col - 2), color):
                        safe = False
                if safe:
                    move = ChessMove(position, Position(row, col - 2))
                    move.additional_move = (
                        Position(row, col - 4),
                        Position(row, col - 1),
                    )
                    moves.append(move)

        return moves

    def initialize_board(self):
        for i in range(8):
            self.squares[6][i] = Pawn("black")
            self.squares[1][i] = Pawn("white")
        self.squares[0][0] = Rook("black")
        self.squares[0][7] = Rook("black")
        self.squares[7][0] = Rook("white")
        self.squares[7][7] = Rook("white")
        self.squares[0][1] = Knight("black")
        self.squares[0][6] = Knight("black")
        self.squares[7][1] = Knight("white")
        self.squares[7][6] = Knight("white")
        self.squares[0][2] = Bishop("black")
        self.squares[0][5] = Bishop("black")
        self.squares[7][2] = Bishop("white")
        self.squares[7][5] = Bishop("white")
        self.squares[0][3] = Queen("black")
        self.squares[7][3] = Queen("white")
        self.squares[2][4] = King("black")
        self.squares[5][4] = King("white")

    def piece_from_position(self, position: Position):
        """
        Get the piece from the given position object
        """
        row, col = position.coordinates()
        if 0 <= row < 8 and 0 <= col < 8:
            return self.squares[row][col]
        return None

    def can_player_move(self, color):
        """
        Check if the given player color (black or white) can make any valid moves.
        Return True if moves are available; otherwise, return False.
        """
        # Check if the king of the specified color is present
        king_exists = any(
            piece and piece.type == "king" and piece.color == color
            for row in self.squares
            for piece in row
        )
        if not king_exists:
            return False

        # Check if the player has any legal moves
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == color:
                    position = Position(row, col)
                    if self.get_available_moves(position):
                        return True
        return False
