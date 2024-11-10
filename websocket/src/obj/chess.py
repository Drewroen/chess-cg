class Piece:
    def __init__(self, color, type=None):
        self.color = color
        self.moved = False
        self.type = type

    def mark_moved(self):
        self.moved = True


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
        self.initialize_board()

    def _letter_to_index(self, letter: str):
        return ord(letter) - 97

    def move(self, first_position: str, second_position: str):
        """
        Move a piece from the first position to the second position
        """
        piece = self.piece_from_chess_notation(first_position)
        self.squares[8 - int(second_position[1])][
            self._letter_to_index(second_position[0])
        ] = piece
        self.squares[8 - int(first_position[1])][
            self._letter_to_index(first_position[0])
        ] = None
        piece.mark_moved()

    def get_available_moves(self, position: str):
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

    def _get_pawn_moves(self, position: str):
        """
        Get the available moves for a pawn in the given position
        """
        piece = self.piece_from_chess_notation(position)
        moves = []
        if piece.color == "white":
            if position[1] == "2":
                if self.squares[5][self._letter_to_index(position[0])] is None:
                    moves.append(f"{position[0]}4")
            if (
                self.squares[8 - int(position[1]) - 1][
                    self._letter_to_index(position[0])
                ]
                is None
            ):
                moves.append(f"{position[0]}{int(position[1]) + 1}")
        else:
            if position[1] == "7":
                if self.squares[2][self._letter_to_index(position[0])] is None:
                    moves.append(f"{position[0]}5")
            if (
                self.squares[8 - int(position[1]) - 1][
                    self._letter_to_index(position[0])
                ]
                is None
            ):
                moves.append(f"{position[0]}{int(position[1]) - 1}")
        return moves

    def _get_rook_moves(self, position: str):
        """
        Get the available moves for a rook in the given position
        """
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves to the right
        for i in range(col + 1, 8):
            if self.squares[row][i] is None:
                moves.append(f"{chr(97+i)}{8-row}")
            else:
                if self.squares[row][i].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+i)}{8-row}")
                break

        # Check moves to the left
        for i in range(col - 1, -1, -1):
            if self.squares[row][i] is None:
                moves.append(f"{chr(97+i)}{8-row}")
            else:
                if self.squares[row][i].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+i)}{8-row}")
                break

        # Check moves upwards
        for i in range(row - 1, -1, -1):
            if self.squares[i][col] is None:
                moves.append(f"{chr(97+col)}{8-i}")
            else:
                if self.squares[i][col].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+col)}{8-i}")
                break

        # Check moves downwards
        for i in range(row + 1, 8):
            if self.squares[i][col] is None:
                moves.append(f"{chr(97+col)}{8-i}")
            else:
                if self.squares[i][col].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+col)}{8-i}")
                break

        return moves

    def _get_knight_moves(self, position: str):
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
                moves.append(f"{chr(97+col+1)}{8-row+2}")
        if row - 1 >= 0 and col + 2 < 8:
            if (
                self.squares[row - 1][col + 2] is None
                or self.squares[row - 1][col + 2].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col+2)}{8-row+1}")

        # Check moves in the second quadrant
        if row - 2 >= 0 and col - 1 >= 0:
            if (
                self.squares[row - 2][col - 1] is None
                or self.squares[row - 2][col - 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-1)}{8-row+2}")
        if row - 1 >= 0 and col - 2 >= 0:
            if (
                self.squares[row - 1][col - 2] is None
                or self.squares[row - 1][col - 2].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-2)}{8-row+1}")

        # Check moves in the third quadrant
        if row + 1 < 8 and col - 2 >= 0:
            if (
                self.squares[row + 1][col - 2] is None
                or self.squares[row + 1][col - 2].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-2)}{8-row-1}")
        if row + 2 < 8 and col - 1 >= 0:
            if (
                self.squares[row + 2][col - 1] is None
                or self.squares[row + 2][col - 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-1)}{8-row-2}")

        # Check moves in the fourth quadrant
        if row + 1 < 8 and col + 2 < 8:
            if (
                self.squares[row + 1][col + 2] is None
                or self.squares[row + 1][col + 2].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col+2)}{8-row-1}")
        if row + 2 < 8 and col + 1 < 8:
            if (
                self.squares[row + 2][col + 1] is None
                or self.squares[row + 2][col + 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col+1)}{8-row-2}")

        return moves

    def _get_bishop_moves(self, position: str):
        """
        Get the available moves for a bishop in the given position
        """
        moves = []
        row, col = 8 - int(position[1]), self._letter_to_index(position[0])

        # Check moves in the first quadrant
        for i in range(1, min(8 - row, 8 - col)):
            if self.squares[row + i][col + i] is None:
                moves.append(f"{chr(97+col+i)}{8-row-i}")
            else:
                if self.squares[row + i][col + i].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+col+i)}{8-row-i}")
                break

        # Check moves in the second quadrant
        for i in range(1, min(8 - row, col + 1)):
            if self.squares[row + i][col - i] is None:
                moves.append(f"{chr(97+col-i)}{8-row-i}")
            else:
                if self.squares[row + i][col - i].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+col-i)}{8-row-i}")
                break

        # Check moves in the third quadrant
        for i in range(1, min(row + 1, col + 1)):
            if self.squares[row - i][col - i] is None:
                moves.append(f"{chr(97+col-i)}{8-row+i}")
            else:
                if self.squares[row - i][col - i].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+col-i)}{8-row+i}")
                break

        # Check moves in the fourth quadrant
        for i in range(1, min(row + 1, 8 - col)):
            if self.squares[row - i][col + i] is None:
                moves.append(f"{chr(97+col+i)}{8-row+i}")
            else:
                if self.squares[row - i][col + i].color != self.squares[row][col].color:
                    moves.append(f"{chr(97+col+i)}{8-row+i}")
                break

        return moves

    def _get_king_moves(self, position: str):
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
                moves.append(f"{chr(97+col+1)}{8-row+1}")
        if row - 1 >= 0:
            if (
                self.squares[row - 1][col] is None
                or self.squares[row - 1][col].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col)}{8-row+1}")

        # Check moves in the second quadrant
        if row - 1 >= 0 and col - 1 >= 0:
            if (
                self.squares[row - 1][col - 1] is None
                or self.squares[row - 1][col - 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-1)}{8-row+1}")
        if col - 1 >= 0:
            if (
                self.squares[row][col - 1] is None
                or self.squares[row][col - 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-1)}{8-row}")

        # Check moves in the third quadrant
        if row + 1 < 8 and col - 1 >= 0:
            if (
                self.squares[row + 1][col - 1] is None
                or self.squares[row + 1][col - 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col-1)}{8-row-1}")
        if row + 1 < 8:
            if (
                self.squares[row + 1][col] is None
                or self.squares[row + 1][col].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col)}{8-row-1}")

        # Check moves in the fourth quadrant
        if row + 1 < 8 and col + 1 < 8:
            if (
                self.squares[row + 1][col + 1] is None
                or self.squares[row + 1][col + 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col+1)}{8-row-1}")
        if col + 1 < 8:
            if (
                self.squares[row][col + 1] is None
                or self.squares[row][col + 1].color != self.squares[row][col].color
            ):
                moves.append(f"{chr(97+col+1)}{8-row}")

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

    def print_board(self):
        """
        Meant for debugging purposes
        """
        for row in self.squares:
            for square in row:
                if square is None:
                    print("☐", end=" ")
                else:
                    if square.color == "black":
                        if square.type == "pawn":
                            print("♟", end=" ")
                        elif square.type == "rook":
                            print("♜", end=" ")
                        elif square.type == "knight":
                            print("♞", end=" ")
                        elif square.type == "bishop":
                            print("♝", end=" ")
                        elif square.type == "queen":
                            print("♛", end=" ")
                        elif square.type == "king":
                            print("♚", end=" ")
                    else:
                        if square.type == "pawn":
                            print("♙", end=" ")
                        elif square.type == "rook":
                            print("♖", end=" ")
                        elif square.type == "knight":
                            print("♘", end=" ")
                        elif square.type == "bishop":
                            print("♗", end=" ")
                        elif square.type == "queen":
                            print("♕", end=" ")
                        elif square.type == "king":
                            print("♔", end=" ")
            print()
