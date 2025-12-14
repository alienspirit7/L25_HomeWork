"""Even/Odd game rules implementation."""
import random
from typing import Tuple, Optional, Dict


class EvenOddRules:
    """Game rules for Even/Odd game."""
    
    def __init__(self):
        self.rng = random.SystemRandom()  # Cryptographically secure random
    
    def validate_choice(self, choice: str) -> Tuple[bool, str]:
        """
        Validate if choice is legal.
        
        Args:
            choice: Player's parity choice
        
        Returns:
            (is_valid, error_message)
        """
        if choice not in ["even", "odd"]:
            return False, f"Invalid choice '{choice}'. Must be 'even' or 'odd' (lowercase)."
        return True, ""
    
    def draw_number(self) -> int:
        """Draw a random number between 1 and 10 (inclusive)."""
        return self.rng.randint(1, 10)
    
    def determine_parity(self, number: int) -> str:
        """Determine if number is even or odd."""
        return "even" if number % 2 == 0 else "odd"
    
    def determine_winner(
        self,
        choice_A: str,
        choice_B: str,
        drawn_number: int
    ) -> Tuple[Optional[str], str]:
        """
        Determine match winner.
        
        Args:
            choice_A: Player A's choice
            choice_B: Player B's choice
            drawn_number: Randomly drawn number
        
        Returns:
            (winner, reason) where winner is "PLAYER_A", "PLAYER_B", or None for draw
        """
        # Same choice = always draw (regardless of number)
        if choice_A == choice_B:
            reason = f"Both chose '{choice_A}' - draw"
            return None, reason
        
        # Determine parity
        parity = self.determine_parity(drawn_number)
        
        # Winner is whoever matches parity
        if choice_A == parity:
            reason = f"Player A chose '{choice_A}', number was {drawn_number} ({parity})"
            return "PLAYER_A", reason
        else:
            reason = f"Player B chose '{choice_B}', number was {drawn_number} ({parity})"
            return "PLAYER_B", reason
    
    def calculate_score(self, winner: Optional[str]) -> Dict[str, int]:
        """
        Calculate match score (points).
        Win: 3 points, Draw: 1 point each, Loss: 0 points
        
        Args:
            winner: "PLAYER_A", "PLAYER_B", or None for draw
        
        Returns:
            Dict mapping player to points
        """
        if winner is None:
            # Draw
            return {"PLAYER_A": 1, "PLAYER_B": 1}
        elif winner == "PLAYER_A":
            # Player A wins
            return {"PLAYER_A": 3, "PLAYER_B": 0}
        else:
            # Player B wins
            return {"PLAYER_A": 0, "PLAYER_B": 3}
