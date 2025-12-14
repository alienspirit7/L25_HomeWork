"""
Data repositories implementing the Repository pattern for runtime data management.

Each repository handles reading, updating, and saving a specific data type.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


# Default data root
DEFAULT_SHARED_ROOT = Path(__file__).parent.parent
DATA_ROOT = DEFAULT_SHARED_ROOT / "data"


class StandingsRepository:
    """Repository for league standings data."""
    
    def __init__(self, league_id: str, data_root: Optional[Path] = None):
        """
        Initialize the standings repository.
        
        Args:
            league_id: League identifier
            data_root: Optional custom data root directory
        """
        self.league_id = league_id
        root = Path(data_root) if data_root else DATA_ROOT
        self.path = root / "leagues" / league_id / "standings.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Load standings from JSON file."""
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "league_id": self.league_id,
                "standings": [],
                "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def save(self, standings: Dict[str, Any]) -> None:
        """Save standings to JSON file."""
        standings["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(standings, f, indent=2, ensure_ascii=False)
    
    def update_player(
        self,
        player_id: str,
        result: str,
        points: int,
    ) -> None:
        """
        Update a player's standings after a match.
        
        Args:
            player_id: Player identifier
            result: Match result ("WIN", "LOSS", "DRAW")
            points: Points earned
        """
        standings = self.load()
        
        # Find or create player entry
        player_entry = None
        for entry in standings["standings"]:
            if entry["player_id"] == player_id:
                player_entry = entry
                break
        
        if not player_entry:
            player_entry = {
                "player_id": player_id,
                "total_points": 0,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
            }
            standings["standings"].append(player_entry)
        
        # Update stats
        player_entry["total_points"] += points
        player_entry["matches_played"] += 1
        
        if result == "WIN":
            player_entry["wins"] += 1
        elif result == "LOSS":
            player_entry["losses"] += 1
        elif result == "DRAW":
            player_entry["draws"] += 1
        
        # Sort by points (descending)
        standings["standings"].sort(
            key=lambda x: (x["total_points"], x["wins"], x["draws"]),
            reverse=True,
        )
        
        self.save(standings)


class RoundsRepository:
    """Repository for rounds history."""
    
    def __init__(self, league_id: str, data_root: Optional[Path] = None):
        """
        Initialize the rounds repository.
        
        Args:
            league_id: League identifier
            data_root: Optional custom data root directory
        """
        self.league_id = league_id
        root = Path(data_root) if data_root else DATA_ROOT
        self.path = root / "leagues" / league_id / "rounds.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Load rounds from JSON file."""
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "league_id": self.league_id,
                "rounds": [],
                "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def save(self, rounds: Dict[str, Any]) -> None:
        """Save rounds to JSON file."""
        rounds["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(rounds, f, indent=2, ensure_ascii=False)
    
    def add_round(self, round_id: int, matches: List[str]) -> None:
        """
        Add a new round to history.
        
        Args:
            round_id: Round number
            matches: List of match IDs in this round
        """
        rounds_data = self.load()
        
        round_entry = {
            "round_id": round_id,
            "matches": matches,
            "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": "in_progress",
        }
        
        rounds_data["rounds"].append(round_entry)
        self.save(rounds_data)
    
    def complete_round(self, round_id: int) -> None:
        """Mark a round as completed."""
        rounds_data = self.load()
        
        for round_entry in rounds_data["rounds"]:
            if round_entry["round_id"] == round_id:
                round_entry["status"] = "completed"
                round_entry["completed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                break
        
        self.save(rounds_data)


class MatchRepository:
    """Repository for individual match data."""
    
    def __init__(self, league_id: str, match_id: str, data_root: Optional[Path] = None):
        """
        Initialize the match repository.
        
        Args:
            league_id: League identifier
            match_id: Match identifier
            data_root: Optional custom data root directory
        """
        self.league_id = league_id
        self.match_id = match_id
        root = Path(data_root) if data_root else DATA_ROOT
        self.path = root / "matches" / league_id / f"{match_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Load match data from JSON file."""
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "match_id": self.match_id,
                "league_id": self.league_id,
                "lifecycle": {},
                "transcript": [],
                "result": None,
            }
        
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def save(self, match_data: Dict[str, Any]) -> None:
        """Save match data to JSON file."""
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(match_data, f, indent=2, ensure_ascii=False)


class PlayerHistoryRepository:
    """Repository for player match history."""
    
    def __init__(self, player_id: str, data_root: Optional[Path] = None):
        """
        Initialize the player history repository.
        
        Args:
            player_id: Player identifier
            data_root: Optional custom data root directory
        """
        self.player_id = player_id
        root = Path(data_root) if data_root else DATA_ROOT
        self.path = root / "players" / player_id / "history.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Load player history from JSON file."""
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "player_id": self.player_id,
                "stats": {
                    "total_matches": 0,
                    "wins": 0,
                    "losses": 0,
                    "draws": 0,
                },
                "matches": [],
            }
        
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def save(self, history: Dict[str, Any]) -> None:
        """Save player history to JSON file."""
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def add_match(
        self,
        match_id: str,
        opponent_id: str,
        result: str,
        my_choice: Optional[str] = None,
        opponent_choice: Optional[str] = None,
    ) -> None:
        """
        Add a match to player history.
        
        Args:
            match_id: Match identifier
            opponent_id: Opponent player ID
            result: Match result ("WIN", "LOSS", "DRAW")
            my_choice: Player's choice in the match
            opponent_choice: Opponent's choice in the match
        """
        history = self.load()
        
        match_entry = {
            "match_id": match_id,
            "opponent_id": opponent_id,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        
        if my_choice:
            match_entry["my_choice"] = my_choice
        if opponent_choice:
            match_entry["opponent_choice"] = opponent_choice
        
        history["matches"].append(match_entry)
        
        # Update stats
        history["stats"]["total_matches"] += 1
        if result == "WIN":
            history["stats"]["wins"] += 1
        elif result == "LOSS":
            history["stats"]["losses"] += 1
        elif result == "DRAW":
            history["stats"]["draws"] += 1
        
        self.save(history)
