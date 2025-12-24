"""Referee Agent - Game Logic Module.

This module contains the match execution logic that uses the game rules
from the league_sdk to determine match outcomes.
"""

import logging
import random
from typing import Dict


def execute_match(
    player_A_id: str,
    player_B_id: str,
    choice_A: str,
    choice_B: str,
    game
) -> Dict:
    """
    Execute a single match using the game rules.
    
    Args:
        player_A_id: First player ID
        player_B_id: Second player ID
        choice_A: Player A's parity choice ("even" or "odd")
        choice_B: Player B's parity choice ("even" or "odd")
        game: EvenOddRules instance from league_sdk
    
    Returns:
        {
            'winner': str or None (for draw),
            'score': {player_A_id: choice_A, player_B_id: choice_B},
            'details': {
                'drawn_number': int,
                'parity': str,
                'outcome': str
            }
        }
    """
    # Validate choices
    valid_choices = ["even", "odd"]
    
    if choice_A not in valid_choices:
        logging.warning(f"Invalid choice from {player_A_id}: {choice_A}, defaulting to 'even'")
        choice_A = "even"
    
    if choice_B not in valid_choices:
        logging.warning(f"Invalid choice from {player_B_id}: {choice_B}, defaulting to 'odd'")
        choice_B = "odd"
    
    # Draw random number using game rules
    drawn_number = game.draw_number()
    
    # Determine winner (EvenOddRules expects choice_A, choice_B, drawn_number)
    winner_result, reason = game.determine_winner(choice_A, choice_B, drawn_number)
    
    # Map PLAYER_A/PLAYER_B to actual player IDs
    if winner_result == "PLAYER_A":
        winner = player_A_id
    elif winner_result == "PLAYER_B":
        winner = player_B_id
    else:
        winner = None  # Draw
    
    # Determine parity of drawn_number
    parity = "even" if drawn_number % 2 == 0 else "odd"
    
    # Determine outcome type
    if winner is None:
        outcome = "DRAW"
    elif winner == player_A_id:
        outcome = "PLAYER_A_WIN"
    else:
        outcome = "PLAYER_B_WIN"
    
    # Calculate points based on outcome (3 for win, 1 for draw, 0 for loss)
    if winner is None:
        # Draw - both get 1 point
        player_A_points = 1
        player_B_points = 1
    elif winner == player_A_id:
        # Player A wins
        player_A_points = 3
        player_B_points = 0
    else:
        # Player B wins
        player_A_points = 0
        player_B_points = 3
    
    result = {
        "winner": winner,
        "score": {
            player_A_id: player_A_points,
            player_B_id: player_B_points
        },
        "details": {
            "drawn_number": drawn_number,
            "parity": parity,
            "outcome": outcome,
            "reason": reason,
            "choices": {
                player_A_id: choice_A,
                player_B_id: choice_B
            }
        }
    }
    
    logging.info(
        f"Match executed: {player_A_id} ({choice_A}) vs {player_B_id} ({choice_B}) "
        f"-> Number: {drawn_number} ({parity}) -> Winner: {winner or 'DRAW'}"
    )
    
    return result


def validate_parity_choice(choice: str) -> bool:
    """
    Validate a parity choice.
    
    Args:
        choice: The parity choice to validate
    
    Returns:
        True if valid ("even" or "odd"), False otherwise
    """
    return choice in ["even", "odd"]
