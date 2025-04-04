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
        additional_move: tuple[Position, Position] = None,
    ):
        self.position_from = position_from
        self.position_to = position_to
        self.position_to_capture = (
            position_to_capture if position_to_capture else position_to
        )
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

    def move(self, position_from: Position, position_to: Position):
        """
        Move a piece from the first position to the second position
        Returns True if the move was successful, False otherwise
        """
        first_position = position_from.notation()
        second_position = position_to.notation()
        available_moves: list[ChessMove] = self.get_available_moves(position_from)
        move: ChessMove = next(
            filter(
                lambda move: move.position_to.notation() == second_position,
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
            self.squares[position_to[0]][position_to[1]] = piece
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

    def get_available_moves(self, position: Position) -> list[ChessMove]:
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
            moves = self._get_king_moves(position)
        return moves

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
                moves.append(ChessMove(position, Position(row - 1, col)))
            # Capture diagonally
            if (
                col - 1 >= 0
                and self.squares[row - 1][col - 1] is not None
                and self.squares[row - 1][col - 1].color != piece.color
            ):
                moves.append(ChessMove(position, Position(row - 1, col - 1)))
            if (
                col + 1 < 8
                and self.squares[row - 1][col + 1] is not None
                and self.squares[row - 1][col + 1].color != piece.color
            ):
                moves.append(ChessMove(position, Position(row - 1, col + 1)))
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
                moves.append(ChessMove(position, Position(row + 1, col)))
            # Capture diagonally
            if (
                col - 1 >= 0
                and self.squares[row + 1][col - 1] is not None
                and self.squares[row + 1][col - 1].color != piece.color
            ):
                moves.append(ChessMove(position, Position(row + 1, col - 1)))
            if (
                col + 1 < 8
                and self.squares[row + 1][col + 1] is not None
                and self.squares[row + 1][col + 1].color != piece.color
            ):
                moves.append(ChessMove(position, Position(row + 1, col + 1)))
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

    def _get_king_moves(self, position: Position) -> list[ChessMove]:
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

        # Check castling moves
        if not self.squares[row][col].moved:  # Ensure the king has not moved
            # Check kingside castling
            if (
                col + 2 < 8
                and self.squares[row][col + 1] is None
                and self.squares[row][col + 2] is None
                and isinstance(self.squares[row][col + 3], Rook)
                and not self.squares[row][col + 3].moved
            ):
                move = ChessMove(position, Position(row, col + 2))
                move.additional_move = (
                    Position(row, col + 3),
                    Position(row, col + 1),
                )
                moves.append(move)

            # Check queenside castling
            if (
                col - 2 >= 0
                and self.squares[row][col - 1] is None
                and self.squares[row][col - 2] is None
                and self.squares[row][col - 3] is None
                and isinstance(self.squares[row][col - 4], Rook)
                and not self.squares[row][col - 4].moved
            ):
                move = ChessMove(position, Position(row, col - 2))
                move.additional_move = (Position(row, col - 4), Position(row, col - 1))
                moves.append(move)

        return moves

    def initialize_board(self):
        for i in range(8):
            self.squares[1][i] = Pawn("black")
            self.squares[6][i] = Pawn("white")
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
        self.squares[0][4] = King("black")
        self.squares[7][4] = King("white")

    def piece_from_position(self, position: Position):
        """
        Get the piece from the given position object
        """
        row, col = position.coordinates()
        if 0 <= row < 8 and 0 <= col < 8:
            return self.squares[row][col]
        return None
