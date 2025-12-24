"""Player strategies for Even/Odd game."""
import random
import logging
from typing import Dict, Optional

def determine_parity_choice(strategy: str, match_info: Dict) -> str:
    """Determine parity choice based on strategy."""
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
    """Randomly choose between 'even' and 'odd'."""
    return random.choice(["even", "odd"])

def always_even_strategy() -> str:
    """Always choose 'even'."""
    return "even"

def always_odd_strategy() -> str:
    """Always choose 'odd'."""
    return "odd"

def alternating_strategy(match_info: Dict) -> str:
    """Alternate between 'even' and 'odd' based on round number."""
    round_id = match_info.get('round_id', 1)
    return "even" if round_id % 2 == 0 else "odd"

def llm_strategy(match_info: Dict, game_history: list = None) -> str:
    """LLM-based strategy using Gemini API. Falls back to random if unavailable."""
    import os
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.warning("GEMINI_API_KEY not found, using random strategy")
        return random_strategy()
    try:
        # TODO: Implement Gemini API call
        # import google.generativeai as genai
        # genai.configure(api_key=api_key)
        # model = genai.GenerativeModel('gemini-pro')
        # prompt = f"Choose 'even' or 'odd' for: {match_info}"
        # response = model.generate_content(prompt)
        logging.info("LLM strategy placeholder - implement with Gemini API")
        return random_strategy()
    except Exception as e:
        logging.error(f"LLM strategy error: {e}, falling back to random")
        return random_strategy()

def adaptive_strategy(match_info: Dict, opponent_id: str, opponent_history: Dict = None) -> str:
    """Learn opponent patterns and counter them."""
    if not opponent_history or opponent_id not in opponent_history:
        return random_strategy()
    choices = opponent_history[opponent_id]
    even_count, odd_count = choices.count("even"), choices.count("odd")
    if even_count > odd_count:
        return "odd"  # opponent prefers even, we choose odd
    elif odd_count > even_count:
        return "even"  # opponent prefers odd, we choose even
    return random_strategy()
