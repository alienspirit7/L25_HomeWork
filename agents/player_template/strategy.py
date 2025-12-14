"""Player Agent - Strategy Module.

This module contains various playing strategies for the Even/Odd game.
Players can use different strategies to make parity choices.
"""

import random
import logging
from typing import Dict, Optional


def determine_parity_choice(strategy: str, match_info: Dict) -> str:
    """
    Determine parity choice based on the configured strategy.
    
    Args:
        strategy: Strategy name ("random", "always_even", "always_odd", "alternating")
        match_info: Current match information
    
    Returns:
        Parity choice: "even" or "odd"
    """
    if strategy == "random":
        return random_strategy()
    elif strategy == "always_even":
        return always_even_strategy()
    elif strategy == "always_odd":
        return always_odd_strategy()
    elif strategy == "alternating":
        return alternating_strategy(match_info)
    else:
        logging.warning(f"Unknown strategy: {strategy}, using random")
        return random_strategy()


def random_strategy() -> str:
    """
    Random strategy: Randomly choose between "even" and "odd".
    
    Returns:
        Random choice: "even" or "odd"
    """
    return random.choice(["even", "odd"])


def always_even_strategy() -> str:
    """
    Always even strategy: Always choose "even".
    
    Returns:
        "even"
    """
    return "even"


def always_odd_strategy() -> str:
    """
    Always odd strategy: Always choose "odd".
    
    Returns:
        "odd"
    """
    return "odd"


def alternating_strategy(match_info: Dict) -> str:
    """
    Alternating strategy: Alternate between "even" and "odd" based on round number.
    
    Args:
        match_info: Current match information (contains round_id)
    
    Returns:
        "even" for even rounds, "odd" for odd rounds
    """
    round_id = match_info.get('round_id', 1)
    return "even" if round_id % 2 == 0 else "odd"


def llm_strategy(match_info: Dict, game_history: list = None) -> str:
    """
    LLM-based strategy: Use language model to make intelligent choice.
    
    This is a placeholder for LLM integration. Implement using:
    - Gemini API
    - OpenAI API
    - Anthropic Claude API
    
    Args:
        match_info: Current match information
        game_history: Previous matches and outcomes
    
    Returns:
        LLM-suggested choice: "even" or "odd"
    """
    # TODO: Implement LLM integration
    # For now, fall back to random
    logging.info("LLM strategy not yet implemented, using random")
    return random_strategy()


def adaptive_strategy(
    match_info: Dict,
    opponent_id: str,
    opponent_history: Dict = None
) -> str:
    """
    Adaptive strategy: Learn opponent's patterns and counter them.
    
    Analyzes opponent's previous choices and tries to predict their next move.
    
    Args:
        match_info: Current match information
        opponent_id: Opponent's player ID
        opponent_history: Dictionary tracking opponent's previous choices
    
    Returns:
        Adaptive choice: "even" or "odd"
    """
    if not opponent_history or opponent_id not in opponent_history:
        # No history available, use random
        return random_strategy()
    
    choices = opponent_history[opponent_id]
    
    # Count opponent's preferences
    even_count = choices.count("even")
    odd_count = choices.count("odd")
    
    # Predict opponent will choose their more frequent choice
    # Then choose the opposite to avoid draws
    if even_count > odd_count:
        # Opponent prefers even, we choose odd
        return "odd"
    elif odd_count > even_count:
        # Opponent prefers odd, we choose even
        return "even"
    else:
        # Opponent is balanced, use random
        return random_strategy()
