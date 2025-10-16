# Plan: Implement Usage Tracking for Limited-Use Modifiers

## Proposed Solution: Track Usage on Piece (Recommended)

Store remaining uses per-modifier on each piece instance, not on the Modifier definition itself.

**Why this approach:**
- Each piece instance needs its own usage counter (e.g., one bishop's Corner Hop is independent of another's)
- Modifier definitions are shared constants, so they shouldn't have mutable state
- Simpler serialization - uses data lives with the piece
- Aligns with existing piece-centric architecture

## Implementation Steps

1. **Update `Modifier` class** (`modifier.py`)
   - Fix `__init__` to store `uses` parameter (currently not stored)
   - Update `to_dict()` to include `uses` field

2. **Update `Piece` class** (`pieces.py`)
   - Add `modifier_uses_remaining: dict[str, int]` to `__init__`
   - Update `add_modifier()` to initialize remaining uses
   - Add `get_modifier_uses_remaining(modifier_type)` method
   - Add `decrement_modifier_uses(modifier_type)` method

3. **Update move generation** (`pieces.py`)
   - In `Bishop.get_possible_moves()`, check `self.get_modifier_uses_remaining("Corner Hop") > 0`
   - Apply same pattern to other limited-use modifiers when implemented

4. **Update `ChessMove` class** (`chess_move.py`)
   - Add optional `used_modifier: str` field to track which modifier enabled the move

5. **Update `Board.move()` method** (`board.py`)
   - After successful move execution, check if `move.used_modifier` exists
   - If so, call `piece.decrement_modifier_uses(move.used_modifier)`

6. **Update board serialization** (`board.py`)
   - Ensure `get_squares()` includes modifier usage data in serialization

## Files to Modify

- `app/obj/modifier.py` - Fix Modifier class to store uses
- `app/obj/pieces.py` - Add usage tracking to Piece, update Bishop.get_possible_moves()
- `app/obj/chess_move.py` - Add used_modifier field
- `app/obj/board.py` - Add usage decrementing in move()
