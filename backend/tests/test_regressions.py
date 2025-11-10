from app.obj.modifier import TELEPORT_MODIFIER
from app.obj.pieces import King
from app.obj.position import position_from_notation
from app.obj.game import Game


def test_bishop_moves_correctly_flake():
    game = Game()
    moves = [
        ("e2", "e4"),
        ("c7", "c6"),
        ("d2", "d4"),
        ("d7", "d5"),
        ("g1", "f3"),
        ("c8", "g4"),
        ("f1", "e2"),
        ("g4", "h5"),
        ("g2", "g4"),
    ]
    for move in moves:
        game.move(
            position_from_notation(move[0]), position_from_notation(move[1]), game.turn
        )

    moves = {
        "moves": {
            "white": [
                (x.position_from.coordinates(), x.position_to.coordinates())
                for x in game.board.get_available_moves_for_color("white")
            ],
            "black": [
                (x.position_from.coordinates(), x.position_to.coordinates())
                for x in game.board.get_available_moves_for_color("black")
            ],
        },
    }

    assert ((3, 7), (4, 6)) in moves["moves"]["black"]
    assert ((3, 7), (2, 6)) in moves["moves"]["black"]


def test_teleport_doesnt_teleport_into_check():
    game = Game()
    piece = game.board.piece_from_position(position_from_notation("e1"))
    assert isinstance(piece, King)

    game.board.piece_from_position(position_from_notation("e1")).add_modifier(
        TELEPORT_MODIFIER
    )
    moves = [
        ("e2", "e4"),
        ("g8", "f6"),
    ]
    for move in moves:
        game.move(
            position_from_notation(move[0]), position_from_notation(move[1]), game.turn
        )

    moves = {
        "moves": {
            "white": [
                (x.position_from.notation(), x.position_to.notation())
                for x in game.board.get_available_moves_for_color("white")
            ],
            "black": [
                (x.position_from.notation(), x.position_to.notation())
                for x in game.board.get_available_moves_for_color("black")
            ],
        },
    }

    assert (("e1", "e4")) not in moves["moves"]["white"]
