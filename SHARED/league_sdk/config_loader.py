"""
Configuration loader implementing lazy loading pattern with caching.

Provides convenient access to all configuration files with automatic caching
and helper methods for searching specific agents.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from .config_models import (
    SystemConfig,
    NetworkConfig,
    SecurityConfig,
    TimeoutsConfig,
    AgentsConfig,
    RefereeConfig,
    PlayerConfig,
    LeagueConfig,
    ScoringConfig,
    ScheduleConfig,
    ParticipantsConfig,
    LeagueSettings,
    GamesRegistry,
    GameTypeConfig,
)


# Default paths - can be overridden
DEFAULT_SHARED_ROOT = Path(__file__).parent.parent
CONFIG_ROOT = DEFAULT_SHARED_ROOT / "config"
DATA_ROOT = DEFAULT_SHARED_ROOT / "data"
LOG_ROOT = DEFAULT_SHARED_ROOT / "logs"


class ConfigLoader:
    """
    Lazy-loading configuration loader with caching.
    
    Loads configuration files only when needed and caches them for
    repeated access. Provides helper methods for searching specific agents.
    """
    
    def __init__(self, shared_root: Optional[Path] = None):
        """
        Initialize the config loader.
        
        Args:
            shared_root: Path to SHARED directory. If None, uses default.
        """
        if shared_root:
            self.root = Path(shared_root) / "config"
        else:
            self.root = CONFIG_ROOT
            
        # Lazy caches
        self._system: Optional[SystemConfig] = None
        self._agents: Optional[AgentsConfig] = None
        self._leagues: Dict[str, LeagueConfig] = {}
        self._games: Optional[GamesRegistry] = None
    
    def load_system(self) -> SystemConfig:
        """Load global system configuration."""
        if self._system:
            return self._system
        
        path = self.root / "system.json"
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._system = SystemConfig(
            schema_version=data["schema_version"],
            system_id=data["system_id"],
            protocol_version=data["protocol_version"],
            default_league_id=data["default_league_id"],
            network=NetworkConfig(**data["network"]),
            security=SecurityConfig(**data["security"]),
            timeouts=TimeoutsConfig(**data["timeouts"]),
            defaults=data.get("defaults", {}),
        )
        return self._system
    
    def load_agents(self) -> AgentsConfig:
        """Load all agents configuration."""
        if self._agents:
            return self._agents
        
        path = self.root / "agents" / "agents_config.json"
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        referees = [RefereeConfig(**ref) for ref in data.get("referees", [])]
        players = [PlayerConfig(**player) for player in data.get("players", [])]
        
        self._agents = AgentsConfig(
            schema_version=data["schema_version"],
            last_updated=data["last_updated"],
            referees=referees,
            players=players,
        )
        return self._agents
    
    def load_league(self, league_id: str) -> LeagueConfig:
        """Load specific league configuration."""
        if league_id in self._leagues:
            return self._leagues[league_id]
        
        path = self.root / "leagues" / f"{league_id}.json"
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        league = LeagueConfig(
            schema_version=data["schema_version"],
            league_id=data["league_id"],
            display_name=data["display_name"],
            game_type=data["game_type"],
            status=data["status"],
            scoring=ScoringConfig(**data["scoring"]),
            schedule=ScheduleConfig(**data["schedule"]),
            participants=ParticipantsConfig(**data["participants"]),
            settings=LeagueSettings(**data["settings"]),
        )
        self._leagues[league_id] = league
        return league
    
    def load_games_registry(self) -> GamesRegistry:
        """Load games registry."""
        if self._games:
            return self._games
        
        path = self.root / "games" / "games_registry.json"
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        games = [GameTypeConfig(**game) for game in data["games"]]
        
        self._games = GamesRegistry(
            schema_version=data["schema_version"],
            last_updated=data["last_updated"],
            games=games,
        )
        return self._games
    
    def get_referee_by_id(self, referee_id: str) -> RefereeConfig:
        """Get a referee configuration by ID."""
        agents = self.load_agents()
        for ref in agents.referees:
            if ref.referee_id == referee_id:
                return ref
        raise ValueError(f"Referee not found: {referee_id}")
    
    def get_player_by_id(self, player_id: str) -> PlayerConfig:
        """Get a player configuration by ID."""
        agents = self.load_agents()
        for player in agents.players:
            if player.player_id == player_id:
                return player
        raise ValueError(f"Player not found: {player_id}")
    
    def get_active_referees(self) -> list[RefereeConfig]:
        """Get all active referees."""
        agents = self.load_agents()
        return [ref for ref in agents.referees if ref.active]
    
    def get_active_players(self) -> list[PlayerConfig]:
        """Get all active players."""
        agents = self.load_agents()
        return [player for player in agents.players if player.active]
