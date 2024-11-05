import src.obj.chess as chess


def test_board_reset():
    board = chess.Board()
    board.reset_board()

    # Assertions for white pieces
    assert board.piece_from_chess_notation("a1").color == "white"
    assert board.piece_from_chess_notation("a1").__class__.__name__ == "Rook"
    assert board.piece_from_chess_notation("b1").color == "white"
    assert board.piece_from_chess_notation("b1").__class__.__name__ == "Knight"
    assert board.piece_from_chess_notation("c1").color == "white"
    assert board.piece_from_chess_notation("c1").__class__.__name__ == "Bishop"
    assert board.piece_from_chess_notation("d1").color == "white"
    assert board.piece_from_chess_notation("d1").__class__.__name__ == "Queen"
    assert board.piece_from_chess_notation("e1").color == "white"
    assert board.piece_from_chess_notation("e1").__class__.__name__ == "King"
    assert board.piece_from_chess_notation("f1").color == "white"
    assert board.piece_from_chess_notation("f1").__class__.__name__ == "Bishop"
    assert board.piece_from_chess_notation("g1").color == "white"
    assert board.piece_from_chess_notation("g1").__class__.__name__ == "Knight"
    assert board.piece_from_chess_notation("h1").color == "white"
    assert board.piece_from_chess_notation("h1").__class__.__name__ == "Rook"
    for i in range(8):
        assert board.piece_from_chess_notation(f"{chr(97+i)}2").color == "white"
        assert (
            board.piece_from_chess_notation(f"{chr(97+i)}2").__class__.__name__
            == "Pawn"
        )

    # Assertions for black pieces
    assert board.piece_from_chess_notation("a8").color == "black"
    assert board.piece_from_chess_notation("a8").__class__.__name__ == "Rook"
    assert board.piece_from_chess_notation("b8").color == "black"
    assert board.piece_from_chess_notation("b8").__class__.__name__ == "Knight"
    assert board.piece_from_chess_notation("c8").color == "black"
    assert board.piece_from_chess_notation("c8").__class__.__name__ == "Bishop"
    assert board.piece_from_chess_notation("d8").color == "black"
    assert board.piece_from_chess_notation("d8").__class__.__name__ == "Queen"
    assert board.piece_from_chess_notation("e8").color == "black"
    assert board.piece_from_chess_notation("e8").__class__.__name__ == "King"
    assert board.piece_from_chess_notation("f8").color == "black"
    assert board.piece_from_chess_notation("f8").__class__.__name__ == "Bishop"
    assert board.piece_from_chess_notation("g8").color == "black"
    assert board.piece_from_chess_notation("g8").__class__.__name__ == "Knight"
    assert board.piece_from_chess_notation("h8").color == "black"
    assert board.piece_from_chess_notation("h8").__class__.__name__ == "Rook"
    for i in range(8):
        assert board.piece_from_chess_notation(f"{chr(97+i)}7").color == "black"
        assert (
            board.piece_from_chess_notation(f"{chr(97+i)}7").__class__.__name__
            == "Pawn"
        )

    # Assertions for empty squares
    for row in range(3, 7):
        for col in range(8):
            assert board.piece_from_chess_notation(f"{chr(97+col)}{row}") is None
