#!/usr/bin/env python3
"""
Script to read and parse PGN files step by step
"""

import os
import re
from typing import Dict, Generator
from app.obj.objects import Position, position_from_notation
from app.obj.game import Game, GameStatus
import pytest


class PGNReader:
    def __init__(self, pgn_file_path: str):
        self.pgn_file_path = pgn_file_path

    def _clean_moves(self, moves_text: str) -> str:
        """Clean moves text to extract only the actual moves without numbers or evaluations"""
        # Remove move numbers (e.g., "1.", "2.", "10.", etc.)
        moves_text = re.sub(r"\b\d+\.", "", moves_text)

        # Remove result annotations (1-0, 0-1, 1/2-1/2)
        moves_text = re.sub(r"\b(1-0|0-1|1/2-1/2)\b", "", moves_text)

        # Remove stockfish evaluations in curly braces {eval}
        moves_text = re.sub(r"\{[^}]*\}", "", moves_text)

        # Remove comments in parentheses
        moves_text = re.sub(r"\([^)]*\)", "", moves_text)

        # Remove annotations like !, ?, !!, ??, !?, ?!
        moves_text = re.sub(r"[!?]+", "", moves_text)

        # Remove any remaining dots
        moves_text = re.sub(r"\.", "", moves_text)

        # Clean up extra whitespace
        moves_text = " ".join(moves_text.split())

        return moves_text.strip()

    def read_first_game(self) -> Dict[str, str]:
        """Read and parse the first game from the PGN file"""
        with open(self.pgn_file_path, "r", encoding="utf-8") as file:
            game_data = {}
            moves = []

            for line in file:
                line = line.strip()

                # Parse metadata (lines starting with [)
                if line.startswith("[") and line.endswith("]"):
                    # Extract key-value pairs like [Event "Rated Classical game"]
                    match = re.match(r'\[(\w+)\s+"([^"]+)"\]', line)
                    if match:
                        key, value = match.groups()
                        game_data[key] = value

                # Parse moves (non-empty lines that don't start with [)
                elif line and not line.startswith("["):
                    moves.append(line)
                    # Break after first game's moves
                    break

            if moves:
                raw_moves = " ".join(moves)
                game_data["moves"] = self._clean_moves(raw_moves)

            return game_data

    def read_games_generator(
        self, limit: int = None
    ) -> Generator[Dict[str, str], None, None]:
        """Generator to read games one by one"""
        with open(self.pgn_file_path, "r", encoding="utf-8") as file:
            game_data = {}
            moves = []
            games_read = 0

            for line in file:
                line = line.strip()

                # If we hit a new [Event line and we already have game data, yield the previous game
                if line.startswith("[Event") and game_data:
                    if moves:
                        raw_moves = " ".join(moves)
                        game_data["moves"] = self._clean_moves(raw_moves)
                    yield game_data
                    games_read += 1

                    if limit and games_read >= limit:
                        break

                    # Reset for new game
                    game_data = {}
                    moves = []

                # Parse metadata
                if line.startswith("[") and line.endswith("]"):
                    match = re.match(r'\[(\w+)\s+"([^"]+)"\]', line)
                    if match:
                        key, value = match.groups()
                        game_data[key] = value

                # Parse moves
                elif line and not line.startswith("["):
                    moves.append(line)

            # Yield the last game (only if we haven't reached the limit)
            if game_data and (not limit or games_read < limit):
                if moves:
                    raw_moves = " ".join(moves)
                    game_data["moves"] = self._clean_moves(raw_moves)
                yield game_data

    def get_file_stats(self) -> Dict[str, any]:
        """Get basic statistics about the PGN file"""
        file_size = os.path.getsize(self.pgn_file_path)

        # Count games by counting [Event lines
        with open(self.pgn_file_path, "r", encoding="utf-8") as file:
            game_count = sum(1 for line in file if line.strip().startswith("[Event"))

        return {
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "total_games": game_count,
            "file_path": self.pgn_file_path,
        }


def get_piece_type_from_pgn_move(move: str) -> str:
    """
    Determine the piece type from a PGN move notation.

    Args:
        move: PGN move notation (e.g., "e4", "Nf3", "Qxd5", "O-O")

    Returns:
        The piece type as a string
    """
    # Handle castling moves
    if move.startswith("O-O"):
        return "king"  # Castling is a king move

    # Remove check (+) and checkmate (#) symbols
    move = move.rstrip("+#")

    # Remove capture notation (x)
    move = move.replace("x", "")

    # Remove promotion notation (=Q, =R, etc.)
    if "=" in move:
        move = move.split("=")[0]

    # Check the first character for piece notation
    first_char = move[0]

    if first_char == "K":
        return "king"
    elif first_char == "Q":
        return "queen"
    elif first_char == "R":
        return "rook"
    elif first_char == "B":
        return "bishop"
    elif first_char == "N":
        return "knight"
    else:
        # If no piece prefix, it's a pawn move
        return "pawn"


def get_notation_from_pgn_move(move: str, color: str) -> str:
    """
    Extract the destination square notation from a PGN move notation.

    Args:
        move: PGN move notation (e.g., "e4", "Nf3", "Qxd5", "O-O", "Ngf6")

    Returns:
        The destination square as a string (e.g., "e4", "f3", "d5")
    """
    # Handle castling moves
    if move.startswith("O-O-O"):
        return "c1" if color == "white" else "c8"
    elif move.startswith("O-O"):
        return "g1" if color == "white" else "g8"

    # Remove check (+) and checkmate (#) symbols
    move = move.rstrip("+#")

    # Handle pawn promotion (e.g., "e8=Q")
    if "=" in move:
        move = move.split("=")[0]

    # The destination square is always the last two characters
    return move[-2:]


def extract_pgn_move(move: str, color: str) -> Dict[str, str]:
    piece_type = get_piece_type_from_pgn_move(move)
    to_square = get_notation_from_pgn_move(move, color)

    is_capture = "x" in move
    is_check = "+" in move
    is_checkmate = "#" in move

    promotion = None
    if "=" in move:
        promotion_letter = move.split("=")[1][0]
        promotion_map = {
            "Q": "queen",
            "R": "rook",
            "B": "bishop",
            "N": "knight",
        }
        promotion = promotion_map.get(promotion_letter, None)

    from_hint_row = None
    from_hint_column = None

    if piece_type != "pawn":
        # Allow optional capture "x" in the regex
        full_source_pattern = r"^[KQRBN]([a-h])([1-8])x?[a-h][1-8]"
        partial_source_pattern = r"^[KQRBN]([a-h]?)([1-8]?)x?[a-h][1-8]"

        match = re.match(full_source_pattern, move)
        if match:
            from_hint_column = match.group(1)
            from_hint_row = match.group(2)
        else:
            match = re.match(partial_source_pattern, move)
            if match:
                from_hint_column = match.group(1) if match.group(1) else None
                from_hint_row = match.group(2) if match.group(2) else None
    else:
        match = re.match(r"^([a-h])x?[a-h][1-8]", move)
        if match:
            from_hint_column = match.group(1) if match.group(1) else None

    return {
        "original_move": move,
        "piece_type": piece_type,
        "from_hint_column": from_hint_column,
        "from_hint_row": from_hint_row,
        "to_square": to_square,
        "is_capture": is_capture,
        "is_check": is_check,
        "is_checkmate": is_checkmate,
        "promotion": promotion,
    }


@pytest.fixture(scope="module")
def pgn_games():
    # Path to the PGN file
    pgn_file = "tests/pgn/lichess_db_standard_rated_2013-01.pgn"

    # Create PGN reader just once
    reader = PGNReader(pgn_file)
    print(reader.get_file_stats())

    # Convert the generator to a list so it can be reused
    games_list = list(reader.read_games_generator())
    return games_list


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
        game.move(position_from_notation(move[0]), position_from_notation(move[1]))

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


@pytest.mark.parametrize("board", range(1, 10001))
def test_read_pgn(pgn_games, board):
    # Get a specific game based on the 'board' parameter (with index bounds checking)
    index = (board - 1) % len(pgn_games)  # Ensure we don't go out of bounds
    pgn_game = pgn_games[index]

    pgn_moves = pgn_game.get("moves", "")
    chess_game = Game()

    for move in pgn_moves.split():
        turn = chess_game.turn
        extracted_pgn = extract_pgn_move(move, chess_game.turn)
        position = find_position_that_can_move_to_position(chess_game, extracted_pgn)
        chess_game.move(
            position,
            position_from_notation(extracted_pgn["to_square"]),
            promote_to=extracted_pgn["promotion"],
        )
        assert (
            turn != chess_game.turn
        ), f"move {move} did not work. Full extracted pgn: {extracted_pgn}. Attempted move: {position.notation()} to {extracted_pgn['to_square']}"
        # Verify all pieces on the board are properly tracked in the pieces list
        for row in range(8):
            for col in range(8):
                piece = chess_game.board.squares[row][col]
                if piece:
                    # Find this piece in the pieces list
                    found = False
                    for tracked_piece in chess_game.board.pieces:
                        if tracked_piece == piece:
                            found = True
                            # Verify position is correct
                            assert (
                                tracked_piece.position.row == row
                                and tracked_piece.position.col == col
                            ), f"Piece position mismatch: {tracked_piece.position.notation()} vs actual {Position(row=row, col=col).notation()}"
                            break
                    assert found, f"{piece.color} {piece.type} at {Position(row=row, col=col).notation()} not found in pieces list"
        if extracted_pgn["is_checkmate"]:
            assert chess_game.status == GameStatus.COMPLETE

    # Add assertions as needed
    assert True


def find_position_that_can_move_to_position(
    game: Game, extracted_pgn: Dict[str, str]
) -> Position:
    """
    Find the initial position of the piece that can move to the target position.

    Args:
        game: The current game state
        extracted_pgn: Dictionary containing information about the move

    Returns:
        The position of the piece that can make the move
    """
    piece_type = extracted_pgn["piece_type"]
    to_square = position_from_notation(extracted_pgn["to_square"])
    from_hint_column = extracted_pgn["from_hint_column"]
    from_hint_row = extracted_pgn["from_hint_row"]

    # Determine the search space based on hints
    if from_hint_column is not None:
        # If we have a column hint, only search that column
        cols_to_search = [ord(from_hint_column) - ord("a")]
    else:
        # Otherwise search all columns
        cols_to_search = list(range(8))

    if from_hint_row is not None:
        # If we have a row hint, only search that row
        rows_to_search = [8 - int(from_hint_row)]
    else:
        # Otherwise search all rows
        rows_to_search = list(range(8))

    # Get all pieces of the current player's turn that match the piece type
    candidates = []
    for row in rows_to_search:
        for col in cols_to_search:
            pos = Position(row=row, col=col)
            piece = game.board.squares[row][col]
            if piece and piece.type == piece_type and piece.color == game.turn:
                # Check if this piece can legally move to the target square
                available_moves = game.board.get_available_moves(pos)
                if to_square.notation() in [
                    move.position_to.notation() for move in available_moves
                ]:
                    candidates.append(pos)

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        # If we still have multiple candidates, we might need additional disambiguation
        # This shouldn't happen with proper PGN notation, but just in case:
        raise Exception(
            f"Multiple candidates found, need more disambiguation. Entire extracted_pgn: {extracted_pgn}"
        )
    else:
        for row in range(8):
            for col in range(8):
                print(
                    game.board.squares[row][col].type
                    if game.board.squares[row][col]
                    else "None",
                    end=" ",
                )
            print()
        raise Exception(
            f"No valid piece found that can move to {extracted_pgn['to_square']}. Entire extracted_pgn: {extracted_pgn}"
        )
