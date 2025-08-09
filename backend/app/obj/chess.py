from app.obj.objects import Piece, Position, Pawn, Rook, Knight, Bishop, Queen, King

BOARD_SIZE = 8
PAWN_START_ROWS = {"white": 6, "black": 1}
PAWN_PROMOTION_ROWS = {"white": 0, "black": 7}
EN_PASSANT_ROWS = {"white": 3, "black": 4}
PAWN_DIRECTIONS = {"white": -1, "black": 1}

KNIGHT_MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
KING_MOVES = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


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
        self.squares: list[list[Piece]] = [
            [None] * BOARD_SIZE for _ in range(BOARD_SIZE)
        ]
        self.last_move: ChessMove = None
        self.pieces: list[Piece] = []
        self.initialize_board()

    def get_squares(self):
        return [
            [
                {"type": piece.type, "color": piece.color} if piece else None
                for piece in row
            ]
            for row in self.squares
        ]

    def _is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def _is_enemy_piece(self, row: int, col: int, color: str) -> bool:
        if not self._is_valid_position(row, col):
            return False
        piece = self.squares[row][col]
        return piece is not None and piece.color != color

    def _is_empty_square(self, row: int, col: int) -> bool:
        if not self._is_valid_position(row, col):
            return False
        return self.squares[row][col] is None

    def kings_in_check(self) -> dict[str, bool]:
        """
        Check if each king is in check.
        Returns a dictionary with keys 'white' and 'black', where the value is True if the king is in check.
        """
        king_positions = {"white": None, "black": None}
        for piece in self.pieces:
            if piece.type == "king":
                if piece.color == "white":
                    king_positions["white"] = piece.position
                elif piece.color == "black":
                    king_positions["black"] = piece.position
                if king_positions["white"] and king_positions["black"]:
                    break

        in_check = {"white": False, "black": False}
        for color, king_pos in king_positions.items():
            if king_pos and self._is_square_attacked(king_pos, color):
                in_check[color] = True
        return in_check

    def is_king_in_check(self, color: str) -> bool:
        """
        Check if the king of the given color is in check.
        """
        king_pos = self._find_king_position(color)
        if not king_pos:
            return False
        return self._is_square_attacked(king_pos, color)

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
        available_moves: list[ChessMove] = self.get_available_moves(
            position_from, ignore_check=False, ignore_illegal_moves=False
        )
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
            piece_to_capture = self.piece_from_position(move.position_to_capture)
            if piece_to_capture:
                self.pieces.remove(piece_to_capture)
            self.squares[position_to[0]][position_to[1]] = move.transform_to or piece
            if move.transform_to:
                move.transform_to.position = Position(position_to[0], position_to[1])
                self.pieces.remove(piece)
                self.pieces.append(move.transform_to)
            else:
                piece.position = Position(position_to[0], position_to[1])
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
                    additional_piece.position = Position(
                        additional_position_to[0], additional_position_to[1]
                    )

            return True

        return False

    def get_available_moves_for_color(self, color: str) -> list[ChessMove]:
        """
        Get all available moves for all pieces of the given color
        """
        moves = []
        for piece in self.pieces:
            if piece.color == color:
                available_moves = self.get_available_moves(
                    piece.position, ignore_check=False, ignore_illegal_moves=False
                )
                moves.extend(available_moves)
        return moves

    def get_available_premoves_for_color(self, color: str) -> list[ChessMove]:
        """
        Get all available moves for all pieces of the given color
        """
        moves = []
        for piece in self.pieces:
            if piece.color == color:
                available_moves = self.get_available_moves(
                    piece.position, ignore_check=True, ignore_illegal_moves=True
                )
                moves.extend(available_moves)
        return moves

    def get_available_moves(
        self,
        position: Position,
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> list[ChessMove]:
        """
        Get the available moves for a piece in the given position
        """
        piece = self.piece_from_position(position)
        if piece is None:
            return []
        moves = []
        if piece.type == "pawn":
            moves = self._get_pawn_moves(position, ignore_illegal_moves)
        if piece.type == "rook":
            moves = self._get_rook_moves(position, ignore_illegal_moves)
        if piece.type == "knight":
            moves = self._get_knight_moves(position, ignore_illegal_moves)
        if piece.type == "bishop":
            moves = self._get_bishop_moves(position, ignore_illegal_moves)
        if piece.type == "queen":
            moves = self._get_rook_moves(
                position, ignore_illegal_moves
            ) + self._get_bishop_moves(position, ignore_illegal_moves)
        if piece.type == "king":
            moves = self._get_king_moves(position, ignore_check, ignore_illegal_moves)

        if not ignore_check:
            moves = [
                m for m in moves if not self._is_king_in_check_after_move(position, m)
            ]

        return moves

    def _find_king_position(self, color: str) -> Position:
        """
        Find the position of the king for the given color.
        Returns the king's position or None if not found.
        """
        for piece in self.pieces:
            if piece.type == "king" and piece.color == color:
                return piece.position
        return None

    def _is_king_in_check_after_move(self, position: Position, move: ChessMove) -> bool:
        """
        Check if the king would be in check after making the given move
        """
        original_piece = self.piece_from_position(position)
        if not original_piece:
            return False

        # Store coordinates for readability
        initial_pos = position.coordinates()
        target_pos = move.position_to.coordinates()
        capture_pos = move.position_to_capture.coordinates()

        # Store original board state
        captured_piece = self.squares[capture_pos[0]][capture_pos[1]]
        temp_piece = self.squares[target_pos[0]][target_pos[1]]

        # Track pieces list changes
        transform_piece = None

        # Apply the move temporarily
        self.squares[initial_pos[0]][initial_pos[1]] = None
        self.squares[capture_pos[0]][capture_pos[1]] = None

        # Handle transformation (promotion)
        if move.transform_to:
            transform_piece = move.transform_to
            self.squares[target_pos[0]][target_pos[1]] = transform_piece
        else:
            self.squares[target_pos[0]][target_pos[1]] = original_piece
            original_piece.position = Position(target_pos[0], target_pos[1])

        # Handle additional moves (e.g., castling)
        additional_state = None
        if move.additional_move:
            additional_from = move.additional_move[0].coordinates()
            additional_to = move.additional_move[1].coordinates()
            additional_piece = self.squares[additional_from[0]][additional_from[1]]
            additional_temp = self.squares[additional_to[0]][additional_to[1]]

            self.squares[additional_to[0]][additional_to[1]] = additional_piece
            self.squares[additional_from[0]][additional_from[1]] = None
            additional_state = (
                additional_from,
                additional_to,
                additional_piece,
                additional_temp,
            )

        # Find king position after the move
        king_position = self._find_king_position(original_piece.color)

        # Check if king is in check
        in_check = king_position and self._is_square_attacked(
            king_position, original_piece.color
        )

        # Restore original board state
        self.squares[initial_pos[0]][initial_pos[1]] = original_piece
        self.squares[target_pos[0]][target_pos[1]] = temp_piece
        self.squares[capture_pos[0]][capture_pos[1]] = captured_piece

        original_piece.position = Position(initial_pos[0], initial_pos[1])

        # Restore additional move if it was made
        if additional_state:
            additional_from, additional_to, additional_piece, additional_temp = (
                additional_state
            )
            self.squares[additional_from[0]][additional_from[1]] = additional_piece
            self.squares[additional_to[0]][additional_to[1]] = additional_temp

        return bool(in_check)

    def _is_square_attacked(self, position: Position, color: str) -> bool:
        """
        Check if a square is attacked by any piece of the opposite color
        """
        row, col = position.coordinates()
        for r in range(8):
            for c in range(8):
                piece = self.squares[r][c]
                if piece and piece.color != color:
                    moves = self.get_available_moves(
                        Position(r, c), ignore_check=True, ignore_illegal_moves=False
                    )
                    for move in moves:
                        if move.position_to.coordinates() == (row, col):
                            return True
        return False

    def chess_notation_from_index(self, row: int, col: int):
        return f"{chr(97+col)}{8-row}"

    def _get_pawn_moves(
        self, position: Position, ignore_illegal_moves: bool = False
    ) -> list[ChessMove]:
        """
        Get all available moves for a pawn at the given position.

        This includes:
        - Forward moves (1 or 2 squares from starting position)
        - Diagonal captures (including promotions)
        - En passant captures
        """
        piece = self.piece_from_position(position)
        row, col = position.coordinates()
        color = piece.color
        direction = PAWN_DIRECTIONS[color]

        moves = []
        moves.extend(
            self._get_pawn_forward_moves(
                position, row, col, color, direction, ignore_illegal_moves
            )
        )
        moves.extend(
            self._get_pawn_capture_moves(
                position, row, col, color, direction, ignore_illegal_moves
            )
        )
        moves.extend(
            self._get_pawn_en_passant_moves(
                position, row, col, color, direction, ignore_illegal_moves
            )
        )

        return moves

    def _get_pawn_forward_moves(
        self,
        position: Position,
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool = False,
    ) -> list[ChessMove]:
        """Get forward moves for a pawn (1 or 2 squares)"""
        moves = []
        target_row = row + direction

        # Check if one square forward is valid and empty
        if not (
            self._is_valid_position(target_row, col)
            and (self._is_empty_square(target_row, col) or ignore_illegal_moves)
        ):
            return moves

        # Handle promotion or regular move
        if target_row == PAWN_PROMOTION_ROWS[color]:
            moves.extend(self._create_promotion_moves(position, target_row, col, color))
        else:
            moves.append(ChessMove(position, Position(target_row, col)))

            # Check for two-square initial move
            if (
                row == PAWN_START_ROWS[color]
                and self._is_valid_position(target_row + direction, col)
                and (
                    self._is_empty_square(target_row + direction, col)
                    or ignore_illegal_moves
                )
            ):
                moves.append(ChessMove(position, Position(target_row + direction, col)))

        return moves

    def _get_pawn_capture_moves(
        self,
        position: Position,
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool = False,
    ) -> list[ChessMove]:
        """Get diagonal capture moves for a pawn"""
        moves = []
        target_row = row + direction

        # Check both diagonal directions
        for col_offset in [-1, 1]:
            target_col = col + col_offset

            if not (
                self._is_valid_position(target_row, target_col)
                and (
                    self._is_enemy_piece(target_row, target_col, color)
                    or ignore_illegal_moves
                )
            ):
                continue

            # Handle promotion or regular capture
            if target_row == PAWN_PROMOTION_ROWS[color]:
                moves.extend(
                    self._create_promotion_moves(
                        position, target_row, target_col, color
                    )
                )
            else:
                moves.append(ChessMove(position, Position(target_row, target_col)))

        return moves

    def _get_pawn_en_passant_moves(
        self,
        position: Position,
        row: int,
        col: int,
        color: str,
        direction: int,
        ignore_illegal_moves: bool = False,
    ) -> list[ChessMove]:
        """Get en passant moves for a pawn"""
        moves = []

        # En passant is only possible from specific rows
        if row != EN_PASSANT_ROWS[color]:
            return moves

        # Check both sides for en passant opportunities
        for col_offset in [-1, 1]:
            target_col = col + col_offset

            if self._is_valid_position(row, target_col) and (
                self._can_capture_en_passant(row, target_col, color)
                or ignore_illegal_moves
            ):
                capture_position = Position(row, target_col)
                move_position = Position(row + direction, target_col)
                moves.append(ChessMove(position, move_position, capture_position))

        return moves

    def _can_capture_en_passant(self, pawn_row: int, pawn_col: int, color: str) -> bool:
        """Check if we can capture en passant at the given position"""
        adjacent_piece = self.squares[pawn_row][pawn_col]

        return (
            adjacent_piece
            and adjacent_piece.type == "pawn"
            and adjacent_piece.color != color
            and self._is_valid_en_passant_move(pawn_row, pawn_col, color)
        )

    def _is_valid_en_passant_move(
        self, pawn_row: int, pawn_col: int, color: str
    ) -> bool:
        """Check if the last move allows en passant capture"""
        if not self.last_move:
            return False

        # Calculate where the enemy pawn should have started and ended for en passant
        enemy_color = self._opposite_color(color)
        start_row = PAWN_START_ROWS[enemy_color]
        end_row = pawn_row

        expected_start = self.chess_notation_from_index(start_row, pawn_col)
        expected_end = self.chess_notation_from_index(end_row, pawn_col)

        return self.last_move == (expected_start, expected_end)

    def _create_promotion_moves(
        self, position: Position, target_row: int, target_col: int, color: str
    ) -> list[ChessMove]:
        """Create all possible promotion moves for a pawn"""
        promotion_pieces = [Bishop(color), Knight(color), Rook(color), Queen(color)]
        return [
            ChessMove(position, Position(target_row, target_col), transform_to=piece)
            for piece in promotion_pieces
        ]

    def _opposite_color(self, color: str) -> str:
        """Get the opposite color"""
        return "black" if color == "white" else "white"

    def _get_sliding_moves(
        self,
        position: Position,
        directions: list[tuple[int, int]],
        ignore_illegal_moves: bool = False,
    ) -> list[ChessMove]:
        moves = []
        row, col = position.coordinates()
        piece = self.piece_from_position(position)

        for dr, dc in directions:
            current_row, current_col = row + dr, col + dc
            while self._is_valid_position(current_row, current_col):
                target_piece = self.squares[current_row][current_col]

                if ignore_illegal_moves:
                    # When ignoring illegal moves, add all valid positions and continue sliding
                    moves.append(
                        ChessMove(position, Position(current_row, current_col))
                    )
                elif target_piece is None:
                    moves.append(
                        ChessMove(position, Position(current_row, current_col))
                    )
                else:
                    if target_piece.color != piece.color:
                        moves.append(
                            ChessMove(position, Position(current_row, current_col))
                        )
                    break
                current_row += dr
                current_col += dc

        return moves

    def _get_rook_moves(
        self, position: Position, ignore_illegal_moves: bool = False
    ) -> list[ChessMove]:
        return self._get_sliding_moves(
            position, [(0, 1), (0, -1), (1, 0), (-1, 0)], ignore_illegal_moves
        )

    def _get_knight_moves(
        self, position: Position, ignore_illegal_moves: bool = False
    ) -> list[ChessMove]:
        moves = []
        row, col = position.coordinates()
        piece = self.piece_from_position(position)

        for dr, dc in KNIGHT_MOVES:
            new_row, new_col = row + dr, col + dc
            if self._is_valid_position(new_row, new_col):
                target_piece = self.squares[new_row][new_col]
                if ignore_illegal_moves or (
                    target_piece is None or target_piece.color != piece.color
                ):
                    moves.append(ChessMove(position, Position(new_row, new_col)))

        return moves

    def _get_bishop_moves(
        self, position: Position, ignore_illegal_moves: bool = False
    ) -> list[ChessMove]:
        return self._get_sliding_moves(
            position, [(1, 1), (1, -1), (-1, -1), (-1, 1)], ignore_illegal_moves
        )

    def _get_king_moves(
        self,
        position: Position,
        ignore_check: bool = False,
        ignore_illegal_moves: bool = False,
    ) -> list[ChessMove]:
        moves = []
        row, col = position.coordinates()
        piece = self.piece_from_position(position)

        # Standard king moves
        for dr, dc in KING_MOVES:
            new_row, new_col = row + dr, col + dc
            if self._is_valid_position(new_row, new_col):
                target_piece = self.squares[new_row][new_col]
                if ignore_illegal_moves or (
                    target_piece is None or target_piece.color != piece.color
                ):
                    moves.append(ChessMove(position, Position(new_row, new_col)))

        # Castling logic
        if (not ignore_check or ignore_illegal_moves) and not piece.moved:
            moves.extend(self._get_castling_moves(position, ignore_illegal_moves))

        return moves

    def _get_castling_moves(
        self, position: Position, ignore_illegal_moves: bool = False
    ) -> list[ChessMove]:
        moves = []
        row, col = position.coordinates()
        piece = self.piece_from_position(position)

        # Kingside castling
        if self._can_castle_kingside(row, col, piece.color) or ignore_illegal_moves:
            move = ChessMove(position, Position(row, col + 2))
            move.additional_move = (Position(row, col + 3), Position(row, col + 1))
            moves.append(move)

        # Queenside castling
        if self._can_castle_queenside(row, col, piece.color) or ignore_illegal_moves:
            move = ChessMove(position, Position(row, col - 2))
            move.additional_move = (Position(row, col - 4), Position(row, col - 1))
            moves.append(move)

        return moves

    def _can_castle_kingside(self, row: int, col: int, color: str) -> bool:
        return (
            col + 2 < BOARD_SIZE
            and self.squares[row][col + 1] is None
            and self.squares[row][col + 2] is None
            and isinstance(self.squares[row][col + 3], Rook)
            and not self.squares[row][col + 3].moved
            and not self._is_square_attacked(Position(row, col), color)
            and not self._is_square_attacked(Position(row, col + 1), color)
            and not self._is_square_attacked(Position(row, col + 2), color)
        )

    def _can_castle_queenside(self, row: int, col: int, color: str) -> bool:
        return (
            col - 2 >= 0
            and self.squares[row][col - 1] is None
            and self.squares[row][col - 2] is None
            and self.squares[row][col - 3] is None
            and isinstance(self.squares[row][col - 4], Rook)
            and not self.squares[row][col - 4].moved
            and not self._is_square_attacked(Position(row, col), color)
            and not self._is_square_attacked(Position(row, col - 1), color)
            and not self._is_square_attacked(Position(row, col - 2), color)
        )

    def initialize_board(self):
        # Set up pawns
        for i in range(8):
            self.squares[1][i] = Pawn("black", Position(1, i))
            self.squares[6][i] = Pawn("white", Position(6, i))

        # Set up rooks
        self.squares[0][0] = Rook("black", Position(0, 0))
        self.squares[0][7] = Rook("black", Position(0, 7))
        self.squares[7][0] = Rook("white", Position(7, 0))
        self.squares[7][7] = Rook("white", Position(7, 7))

        # Set up knights
        self.squares[0][1] = Knight("black", Position(0, 1))
        self.squares[0][6] = Knight("black", Position(0, 6))
        self.squares[7][1] = Knight("white", Position(7, 1))
        self.squares[7][6] = Knight("white", Position(7, 6))

        # Set up bishops
        self.squares[0][2] = Bishop("black", Position(0, 2))
        self.squares[0][5] = Bishop("black", Position(0, 5))
        self.squares[7][2] = Bishop("white", Position(7, 2))
        self.squares[7][5] = Bishop("white", Position(7, 5))

        # Set up queens
        self.squares[0][3] = Queen("black", Position(0, 3))
        self.squares[7][3] = Queen("white", Position(7, 3))

        # Set up kings
        self.squares[0][4] = King("black", Position(0, 4))
        self.squares[7][4] = King("white", Position(7, 4))

        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece:
                    self.pieces.append(piece)

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
        king_exists = self.pieces and any(
            piece.type == "king" and piece.color == color for piece in self.pieces
        )
        if not king_exists:
            return False

        # Check if the player has any legal moves
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece and piece.color == color:
                    position = Position(row, col)
                    if self.get_available_moves(
                        position, ignore_check=False, ignore_illegal_moves=False
                    ):
                        return True
        return False
