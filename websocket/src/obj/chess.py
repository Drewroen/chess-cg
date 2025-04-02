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
        self, position_to_move: Position, position_to_capture: Position = None
    ):
        self.position_to_move = position_to_move
        self.position_to_capture = (
            position_to_capture if position_to_capture else position_to_move
        )

    def to_dict(self):
        return {
            "position_to_move": self.position_to_move.to_dict(),
            "position_to_capture": self.position_to_capture.to_dict(),
        }


class Board:
    def get_squares(self):
        return [
            [
                {"type": piece.type, "color": piece.color} if piece else None
                for piece in row
            ]
            for row in self.squares
        ]

    def __init__(self):
        self.squares: list[list[Piece]] = [[None] * 8 for _ in range(8)]
        self.last_move = None
        self.initialize_board()

    def _letter_to_index(self, letter: str):
        return ord(letter) - 97

    def move(self, position_from: Position, position_to: Position):
        """
        Move a piece from the first position to the second position
        Returns True if the move was successful, False otherwise
        """
        first_position = position_from.notation()
        second_position = position_to.notation()
        available_moves: list[ChessMove] = self.get_available_moves(first_position)
        move: ChessMove = next(
            filter(
                lambda move: move.position_to_move.notation() == second_position,
                available_moves,
            ),
            None,
        )

        if move:
            initial_position = position_from.coordinates()
            position_to_move = move.position_to_move.coordinates()
            position_to_capture = move.position_to_capture.coordinates()

            piece = self.piece_from_chess_notation(first_position)
            self.squares[position_to_capture[0]][position_to_capture[1]] = None
            self.squares[position_to_move[0]][position_to_move[1]] = piece
            self.squares[initial_position[0]][initial_position[1]] = None
            piece.mark_moved()
            self.last_move = (first_position, second_position)
            return True

        return False

    def get_available_moves(self, position: str) -> list[ChessMove]:
        """
        Get the available moves for a piece in the given position
        """
        piece = self.piece_from_chess_notation(position)
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

    def position_from_index(self, row: int, col: int):
        return Position(row, col)

    def index_from_chess_notation(self, notation: str):
        return 8 - int(notation[1]), self._letter_to_index(notation[0])

    def _get_pawn_moves(self, position: str) -> list[ChessMove]:
        """
        Get the available moves for a pawn in the given position
        """
        piece = self.piece_from_chess_notation(position)
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves for white pawns
        if piece.color == "white":
            # If the pawn is in its initial position, it can move two squares forward
            if row == 6:
                if self.squares[4][col] is None and self.squares[5][col] is None:
                    moves.append(ChessMove(self.position_from_index(4, col)))
            # Move one square forward if the square is empty
            if self.squares[row - 1][col] is None:
                moves.append(ChessMove(self.position_from_index(row - 1, col)))
            # Capture diagonally
            if (
                col - 1 >= 0
                and self.squares[row - 1][col - 1] is not None
                and self.squares[row - 1][col - 1].color != piece.color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col - 1)))
            if (
                col + 1 < 8
                and self.squares[row - 1][col + 1] is not None
                and self.squares[row - 1][col + 1].color != piece.color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col + 1)))
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
                            self.position_from_index(row - 1, col - 1),
                            self.position_from_index(row, col - 1),
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
                            self.position_from_index(row - 1, col + 1),
                            self.position_from_index(row, col + 1),
                        )
                    )
        else:
            # Check moves for black pawns
            # If the pawn is in its initial position, it can move two squares forward
            if row == 1:
                if self.squares[3][col] is None and self.squares[2][col] is None:
                    moves.append(ChessMove(self.position_from_index(3, col)))
            # Move one square forward if the square is empty
            if self.squares[row + 1][col] is None:
                moves.append(ChessMove(self.position_from_index(row + 1, col)))
            # Capture diagonally
            if (
                col - 1 >= 0
                and self.squares[row + 1][col - 1] is not None
                and self.squares[row + 1][col - 1].color != piece.color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col - 1)))
            if (
                col + 1 < 8
                and self.squares[row + 1][col + 1] is not None
                and self.squares[row + 1][col + 1].color != piece.color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col + 1)))
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
                            self.position_from_index(row + 1, col - 1),
                            self.position_from_index(row, col - 1),
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
                            self.position_from_index(row + 1, col + 1),
                            self.position_from_index(row, col + 1),
                        )
                    )

        return moves

    def _get_rook_moves(self, position: str) -> list[ChessMove]:
        """
        Get the available moves for a rook in the given position
        """
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves to the right
        for i in range(col + 1, 8):
            if self.squares[row][i] is None:
                moves.append(ChessMove(self.position_from_index(row, i)))
            else:
                if self.squares[row][i].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(row, i)))
                break

        # Check moves to the left
        for i in range(col - 1, -1, -1):
            if self.squares[row][i] is None:
                moves.append(ChessMove(self.position_from_index(row, i)))
            else:
                if self.squares[row][i].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(row, i)))
                break

        # Check moves upwards
        for i in range(row - 1, -1, -1):
            if self.squares[i][col] is None:
                moves.append(ChessMove(self.position_from_index(i, col)))
            else:
                if self.squares[i][col].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(i, col)))
                break

        # Check moves downwards
        for i in range(row + 1, 8):
            if self.squares[i][col] is None:
                moves.append(ChessMove(self.position_from_index(i, col)))
            else:
                if self.squares[i][col].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(i, col)))
                break

        return moves

    def _get_knight_moves(self, position: str) -> list[ChessMove]:
        """
        Get the available moves for a knight in the given position
        """
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves in the first quadrant
        if row - 2 >= 0 and col + 1 < 8:
            if (
                self.squares[row - 2][col + 1] is None
                or self.squares[row - 2][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 2, col + 1)))
        if row - 1 >= 0 and col + 2 < 8:
            if (
                self.squares[row - 1][col + 2] is None
                or self.squares[row - 1][col + 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col + 2)))

        # Check moves in the second quadrant
        if row - 2 >= 0 and col - 1 >= 0:
            if (
                self.squares[row - 2][col - 1] is None
                or self.squares[row - 2][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 2, col - 1)))
        if row - 1 >= 0 and col - 2 >= 0:
            if (
                self.squares[row - 1][col - 2] is None
                or self.squares[row - 1][col - 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col - 2)))

        # Check moves in the third quadrant
        if row + 1 < 8 and col - 2 >= 0:
            if (
                self.squares[row + 1][col - 2] is None
                or self.squares[row + 1][col - 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col - 2)))
        if row + 2 < 8 and col - 1 >= 0:
            if (
                self.squares[row + 2][col - 1] is None
                or self.squares[row + 2][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 2, col - 1)))

        # Check moves in the fourth quadrant
        if row + 1 < 8 and col + 2 < 8:
            if (
                self.squares[row + 1][col + 2] is None
                or self.squares[row + 1][col + 2].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col + 2)))
        if row + 2 < 8 and col + 1 < 8:
            if (
                self.squares[row + 2][col + 1] is None
                or self.squares[row + 2][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 2, col + 1)))

        return moves

    def _get_bishop_moves(self, position: str) -> list[ChessMove]:
        """
        Get the available moves for a bishop in the given position
        """
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves in the first quadrant
        for i in range(1, min(8 - row, 8 - col)):
            if self.squares[row + i][col + i] is None:
                moves.append(ChessMove(self.position_from_index(row + i, col + i)))
            else:
                if self.squares[row + i][col + i].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(row + i, col + i)))
                break

        # Check moves in the second quadrant
        for i in range(1, min(8 - row, col + 1)):
            if self.squares[row + i][col - i] is None:
                moves.append(ChessMove(self.position_from_index(row + i, col - i)))
            else:
                if self.squares[row + i][col - i].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(row + i, col - i)))
                break

        # Check moves in the third quadrant
        for i in range(1, min(row + 1, col + 1)):
            if self.squares[row - i][col - i] is None:
                moves.append(ChessMove(self.position_from_index(row - i, col - i)))
            else:
                if self.squares[row - i][col - i].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(row - i, col - i)))
                break

        # Check moves in the fourth quadrant
        for i in range(1, min(row + 1, 8 - col)):
            if self.squares[row - i][col + i] is None:
                moves.append(ChessMove(self.position_from_index(row - i, col + i)))
            else:
                if self.squares[row - i][col + i].color != self.squares[row][col].color:
                    moves.append(ChessMove(self.position_from_index(row - i, col + i)))
                break

        return moves

    def _get_king_moves(self, position: str) -> list[ChessMove]:
        """
        Get the available moves for a king in the given position
        """
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves in the first quadrant
        if row - 1 >= 0 and col + 1 < 8:
            if (
                self.squares[row - 1][col + 1] is None
                or self.squares[row - 1][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col + 1)))
        if row - 1 >= 0:
            if (
                self.squares[row - 1][col] is None
                or self.squares[row - 1][col].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col)))

        # Check moves in the second quadrant
        if row - 1 >= 0 and col - 1 >= 0:
            if (
                self.squares[row - 1][col - 1] is None
                or self.squares[row - 1][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row - 1, col - 1)))
        if col - 1 >= 0:
            if (
                self.squares[row][col - 1] is None
                or self.squares[row][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row, col - 1)))

        # Check moves in the third quadrant
        if row + 1 < 8 and col - 1 >= 0:
            if (
                self.squares[row + 1][col - 1] is None
                or self.squares[row + 1][col - 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col - 1)))
        if row + 1 < 8:
            if (
                self.squares[row + 1][col] is None
                or self.squares[row + 1][col].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col)))

        # Check moves in the fourth quadrant
        if row + 1 < 8 and col + 1 < 8:
            if (
                self.squares[row + 1][col + 1] is None
                or self.squares[row + 1][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row + 1, col + 1)))
        if col + 1 < 8:
            if (
                self.squares[row][col + 1] is None
                or self.squares[row][col + 1].color != self.squares[row][col].color
            ):
                moves.append(ChessMove(self.position_from_index(row, col + 1)))

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

    def piece_from_chess_notation(self, notation: str):
        """
        Get the piece based on the chess notation
        """
        letter, number = notation[0], int(notation[1])
        return self.squares[8 - number][self._letter_to_index(letter)]
