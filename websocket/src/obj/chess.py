class Piece:
    def __init__(self, color):
        self.color = color
        self.moved = False

    def move(self):
        self.moved = True


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)


class King(Piece):
    def __init__(self, color):
        super().__init__(color)


class Board:
    def __init__(self):
        self.squares: list[list[Piece]] = [[None] * 8 for _ in range(8)]

    def _letter_to_index(self, letter: str):
        return ord(letter) - 97

    def reset_board(self):
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
                        if square.__class__.__name__ == "Pawn":
                            print("♟", end=" ")
                        elif square.__class__.__name__ == "Rook":
                            print("♜", end=" ")
                        elif square.__class__.__name__ == "Knight":
                            print("♞", end=" ")
                        elif square.__class__.__name__ == "Bishop":
                            print("♝", end=" ")
                        elif square.__class__.__name__ == "Queen":
                            print("♛", end=" ")
                        elif square.__class__.__name__ == "King":
                            print("♚", end=" ")
                    else:
                        if square.__class__.__name__ == "Pawn":
                            print("♙", end=" ")
                        elif square.__class__.__name__ == "Rook":
                            print("♖", end=" ")
                        elif square.__class__.__name__ == "Knight":
                            print("♘", end=" ")
                        elif square.__class__.__name__ == "Bishop":
                            print("♗", end=" ")
                        elif square.__class__.__name__ == "Queen":
                            print("♕", end=" ")
                        elif square.__class__.__name__ == "King":
                            print("♔", end=" ")
            print()
