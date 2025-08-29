"""ELO rating calculation service."""

import logging
from typing import Optional

from .database_service import DatabaseService


class EloService:
    """Service for calculating and updating ELO ratings."""
    
    K_FACTOR = 24
    DEFAULT_RATING = 1200

    def calculate_rating_change(
        self, player_rating: int, opponent_rating: int, result: str
    ) -> int:
        """
        Calculate ELO rating change for a player using standard ELO formula.

        Args:
            player_rating: Current rating of the player
            opponent_rating: Current rating of the opponent
            result: 'win', 'loss', or 'draw'

        Returns:
            Rating change (positive or negative)
        """
        # Convert result to score
        if result == "win":
            actual_score = 1.0
        elif result == "draw":
            actual_score = 0.5
        elif result == "loss":
            actual_score = 0.0
        else:
            raise ValueError("Result must be 'win', 'loss', or 'draw'")

        # Calculate expected score
        rating_diff = opponent_rating - player_rating
        expected_score = 1 / (1 + 10 ** (rating_diff / 400))

        # Calculate rating change
        rating_change = self.K_FACTOR * (actual_score - expected_score)

        return round(rating_change)

    async def update_ratings(
        self, 
        white_id: str, 
        black_id: str, 
        winner: str,
        get_user_info_func,
        db_service: DatabaseService
    ) -> Optional[tuple[int, int]]:
        """
        Update ELO ratings for both players after a completed game.
        
        Args:
            white_id: White player ID
            black_id: Black player ID  
            winner: 'white', 'black', or 'draw'
            get_user_info_func: Function to get user info
            db_service: Database service instance
            
        Returns:
            Tuple of (white_rating_change, black_rating_change) or None if skipped
        """
        # Skip rating updates for guest players
        if white_id.startswith("guest_") or black_id.startswith("guest_"):
            logging.info("Skipping ELO updates for guest players")
            return None

        try:
            # Get current ratings
            white_info = await get_user_info_func(white_id)
            black_info = await get_user_info_func(black_id)
            white_elo = white_info["elo"] or self.DEFAULT_RATING
            black_elo = black_info["elo"] or self.DEFAULT_RATING

            # Determine results for each player
            if winner == "white":
                white_result = "win"
                black_result = "loss"
            elif winner == "black":
                white_result = "loss"
                black_result = "win"
            elif winner == "draw":
                white_result = "draw"
                black_result = "draw"
            else:
                logging.warning(f"Unknown game winner: {winner}, skipping ELO updates")
                return None

            # Calculate rating changes
            white_change = self.calculate_rating_change(white_elo, black_elo, white_result)
            black_change = self.calculate_rating_change(black_elo, white_elo, black_result)

            # Update ratings in database
            new_white_elo = white_elo + white_change
            new_black_elo = black_elo + black_change

            await db_service.update_user_elo(white_id, new_white_elo)
            await db_service.update_user_elo(black_id, new_black_elo)

            logging.info(
                f"ELO updated - White: {white_elo} → {new_white_elo} ({white_change:+d}), "
                f"Black: {black_elo} → {new_black_elo} ({black_change:+d})"
            )
            
            return (white_change, black_change)

        except Exception as e:
            logging.error(f"Failed to update ELO ratings: {e}")
            return None