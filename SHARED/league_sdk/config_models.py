"""
Configuration dataclass models for the League SDK.

These models provide type-safe access to configuration data loaded from JSON files.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class NetworkConfig:
    """Network configuration settings."""
    base_host: str
    default_league_manager_port: int
    default_referee_port_range: List[int]
    default_player_port_range: List[int]


@dataclass
class SecurityConfig:
    """Security and authentication settings."""
    enable_auth_tokens: bool
    token_length: int
    token_ttl_hours: int


@dataclass
class TimeoutsConfig:
    """Timeout settings for various operations."""
    register_referee_timeout_sec: int
    register_player_timeout_sec: int
    game_join_ack_timeout_sec: int
    move_timeout_sec: int
    generic_response_timeout_sec: int


@dataclass
class SystemConfig:
    """Global system configuration."""
    schema_version: str
    system_id: str
    protocol_version: str
    default_league_id: str
    network: NetworkConfig
    security: SecurityConfig
    timeouts: TimeoutsConfig
    defaults: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefereeConfig:
    """Referee agent configuration."""
    referee_id: str
    display_name: str
    endpoint: str
    version: str
    game_types: List[str]
    max_concurrent_matches: int
    active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayerConfig:
    """Player agent configuration."""
    player_id: str
    display_name: str
    version: str
    preferred_leagues: List[str]
    game_types: List[str]
    default_endpoint: str
    strategy: str = "random"
    active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentsConfig:
    """Configuration for all agents in the system."""
    schema_version: str
    last_updated: str
    referees: List[RefereeConfig]
    players: List[PlayerConfig]


@dataclass
class ScoringConfig:
    """League scoring configuration."""
    win_points: int
    draw_points: int
    loss_points: int
    technical_loss_points: int
    tiebreakers: List[str]


@dataclass
class ScheduleConfig:
    """League scheduling configuration."""
    format: str  # e.g., "round_robin"
    rounds_per_matchup: int
    parallel_matches: bool


@dataclass
class ParticipantsConfig:
    """League participants configuration."""
    min_players: int
    max_players: int
    registered_players: List[str] = field(default_factory=list)


@dataclass
class LeagueSettings:
    """League-specific settings."""
    registration_timeout_sec: int
    auto_start_when_ready: bool
    publish_standings_after_round: bool


@dataclass
class LeagueConfig:
    """League-specific configuration."""
    schema_version: str
    league_id: str
    display_name: str
    game_type: str
    status: str
    scoring: ScoringConfig
    schedule: ScheduleConfig
    participants: ParticipantsConfig
    settings: LeagueSettings


@dataclass
class GameTypeConfig:
    """Game type definition."""
    game_type: str
    display_name: str
    description: str
    version: str
    min_players: int
    max_players: int
    rules_reference: str
    valid_moves: List[str]
    outcomes: List[str]


@dataclass
class GamesRegistry:
    """Registry of available game types."""
    schema_version: str
    last_updated: str
    games: List[GameTypeConfig]
