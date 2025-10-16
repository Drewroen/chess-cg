# Unimplemented Modifiers

This document tracks modifiers that have been defined but not yet implemented in the game logic.

## Queen Modifiers

### Infiltration
- **Score**: 3
- **Uses**: 1 (limited use)
- **Description**: This piece may move to any open space on your opponent's home row
- **Implementation needed**: Add special move to any empty square on opponent's back rank

## King Modifiers

### EscapeHatch
- **Score**: 3
- **Uses**: 1 (limited use)
- **Description**: This piece may move to any unoccupied square on the home row
- **Implementation needed**: Add special move to any empty square on king's starting rank

### AggressiveKing
- **Score**: 4
- **Uses**: 1 (limited use)
- **Description**: This piece may move up to two squares in any direction
- **Implementation needed**: Extend king moves to include 2-square radius

### Teleport
- **Score**: 4
- **Uses**: 1 (limited use)
- **Description**: This piece may swap places with any friendly piece on the board
- **Implementation needed**: Add special move to swap with any friendly piece

## Implementation Notes

- Limited use modifiers (uses=1) will require additional tracking to ensure they can only be used once per game
- Special moves (Corner Hop, Infiltration, EscapeHatch, Teleport) may need new move validation logic
- SacrificialQueen requires checking if the king is currently in check
