"""Helper utility functions."""
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Tuple


def get_iso_timestamp() -> str:
    """Generate ISO-8601 timestamp with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_conversation_id(prefix: str = "conv") -> str:
    """Generate unique conversation ID."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_match_id(round_id: int, match_num: int) -> str:
    """Generate match ID (e.g., R1M1, R2M3)."""
    return f"R{round_id}M{match_num}"


def validate_parity_choice(choice: str) -> bool:
    """Validate parity choice is exactly 'even' or 'odd'."""
    return choice in ["even", "odd"]


def generate_round_robin_schedule(player_ids: List[str]) -> List[Tuple[str, str, int, int]]:
    """
    Generate round-robin schedule for players.
    Returns: List of (player_A_id, player_B_id, round_id, match_num)
    """
    n = len(player_ids)
    matches = []
    match_counter = 1
    
    # Round-robin algorithm
    for round_id in range(1, n):
        for i in range(n // 2):
            j = n - 1 - i
            if i != j:  # Skip self-matches
                player_A = player_ids[i]
                player_B = player_ids[j]
                matches.append((player_A, player_B, round_id, match_counter))
                match_counter += 1
        
        # Rotate players (keep first fixed)
        player_ids = [player_ids[0]] + [player_ids[-1]] + player_ids[1:-1]
    
    return matches


def calculate_standings(results: Dict[str, Dict]) -> List[Dict]:
    """
    Calculate league standings from match results.
    Tie-breaking: points -> wins -> draws -> alphabetical
    """
    stats = {}
    
    # Initialize stats for all players
    for match_id, result in results.items():
        for player_id in result['score'].keys():
            if player_id not in stats:
                stats[player_id] = {
                    'player_id': player_id,
                    'played': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'points': 0
                }
    
    # Calculate statistics
    for match_id, result in results.items():
        winner = result.get('winner')
        for player_id, points in result['score'].items():
            stats[player_id]['played'] += 1
            stats[player_id]['points'] += points
            
            if winner is None:  # Draw
                stats[player_id]['draws'] += 1
            elif winner == player_id:  # Win
                stats[player_id]['wins'] += 1
            else:  # Loss
                stats[player_id]['losses'] += 1
    
    # Sort by: points (desc), wins (desc), draws (desc), player_id (asc)
    standings = sorted(
        stats.values(),
        key=lambda x: (-x['points'], -x['wins'], -x['draws'], x['player_id'])
    )
    
    # Add rank
    for rank, entry in enumerate(standings, start=1):
        entry['rank'] = rank
    
    return standings


def determine_parity(number: int) -> str:
    """Determine if number is even or odd."""
    return "even" if number % 2 == 0 else "odd"
