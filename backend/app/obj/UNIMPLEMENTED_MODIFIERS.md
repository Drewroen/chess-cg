# Unimplemented Modifiers

This document tracks modifiers that have been defined but not yet implemented in the game logic.

## Knight Modifiers

### Longhorn
- **Score**: 3
- **Description**: This piece can also move two squares in a straight line
- **Implementation needed**: Add straight-line two-square moves to Knight.get_possible_moves()

### Pegasus
- **Score**: 4
- **Description**: This piece may also move in an L shape with 2 squares in each direction
- **Implementation needed**: Add extended L-shaped moves (2x2 instead of 2x1) to Knight.get_possible_moves()

### RoyalGuard
- **Score**: 3
- **Description**: This piece may also move like a king
- **Implementation needed**: Add king moves to Knight.get_possible_moves()

## Queen Modifiers

### SacrificialQueen
- **Score**: 4
- **Uses**: 1 (limited use)
- **Description**: This piece may move anywhere if the king is in check
- **Implementation needed**: Add teleport-to-any-square when king is in check in Queen.get_possible_moves()

### Kneen
- **Score**: 4
- **Description**: This piece combines the movement of a Queen and a Knight
- **Implementation needed**: Add knight moves to Queen.get_possible_moves()

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
