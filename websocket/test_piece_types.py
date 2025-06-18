#!/usr/bin/env python3
"""
Test script to verify piece type identification from PGN moves
"""

from read_pgn import get_piece_type_from_pgn_move


def test_piece_types():
    """Test various PGN move notations"""
    test_moves = [
        # Pawn moves
        ("e4", "pawn"),
        ("e5", "pawn"),
        ("exd5", "pawn"),
        ("a8=Q", "pawn"),  # Promotion
        ("dxc6", "pawn"),
        # Piece moves
        ("Nf3", "knight"),
        ("Nc6", "knight"),
        ("Nxd5", "knight"),
        ("Bb5", "bishop"),
        ("Bxf7+", "bishop"),
        ("Ra1", "rook"),
        ("Rxh8", "rook"),
        ("Qd4", "queen"),
        ("Qxe7#", "queen"),
        ("Kg1", "king"),
        ("Kxf2", "king"),
        # Castling
        ("O-O", "king"),
        ("O-O-O", "king"),
        # With check/checkmate
        ("Qh5+", "queen"),
        ("Rxf8#", "rook"),
        ("Nf7+", "knight"),
    ]

    print("Testing piece type identification:")
    print("-" * 40)

    for move, expected in test_moves:
        result = get_piece_type_from_pgn_move(move)
        status = "✓" if result == expected else "✗"
        print(f"{status} {move:8} -> {result:8} (expected: {expected})")


if __name__ == "__main__":
    test_piece_types()
