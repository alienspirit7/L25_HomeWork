"""
League SDK - Python library for AI Agent League system.

This package provides a clean abstraction layer between JSON configuration files
and agent code, implementing dataclasses for type safety and the Repository pattern
for data access.
"""

from .config_models import (
    SystemConfig,
    NetworkConfig,
    SecurityConfig,
    TimeoutsConfig,
    RefereeConfig,
    PlayerConfig,
    LeagueConfig,
    ScoringConfig,
)
from .config_loader import ConfigLoader
from .logger import JsonLogger
from .repositories import (
    StandingsRepository,
    RoundsRepository,
    MatchRepository,
    PlayerHistoryRepository,
)

__version__ = "1.0.0"

__all__ = [
    "SystemConfig",
    "NetworkConfig",
    "SecurityConfig",
    "TimeoutsConfig",
    "RefereeConfig",
    "PlayerConfig",
    "LeagueConfig",
    "ScoringConfig",
    "ConfigLoader",
    "JsonLogger",
    "StandingsRepository",
    "RoundsRepository",
    "MatchRepository",
    "PlayerHistoryRepository",
]
