"""
JSONL logger for structured logging.

Implements JSON Lines format where each log entry is a separate JSON object on its own line.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any


# Default log root
DEFAULT_SHARED_ROOT = Path(__file__).parent.parent
LOG_ROOT = DEFAULT_SHARED_ROOT / "logs"


class JsonLogger:
    """
    Structured logger using JSONL (JSON Lines) format.
    
    Each log entry is a complete JSON object on a single line, enabling:
    - Efficient append-only logging
    - Easy parsing and analysis
    - Real-time streaming
    """
    
    def __init__(
        self,
        component: str,
        league_id: Optional[str] = None,
        log_root: Optional[Path] = None,
    ):
        """
        Initialize the JSON logger.
        
        Args:
            component: Component name (e.g., "league_manager", "referee:REF01")
            league_id: Optional league ID for league-specific logs
            log_root: Optional custom log root directory
        """
        self.component = component
        self.league_id = league_id
        
        # Determine log directory
        root = Path(log_root) if log_root else LOG_ROOT
        
        if league_id:
            subdir = root / "league" / league_id
        elif ":" in component:  # Agent-specific log
            subdir = root / "agents"
        else:  # System log
            subdir = root / "system"
        
        subdir.mkdir(parents=True, exist_ok=True)
        
        # Create log file name
        safe_component = component.replace(":", "_").replace("/", "_")
        self.log_file = subdir / f"{safe_component}.log.jsonl"
    
    def log(
        self,
        event_type: str,
        level: str = "INFO",
        **details: Any,
    ) -> None:
        """
        Log an event with structured data.
        
        Args:
            event_type: Type of event (e.g., "MESSAGE_SENT", "GAME_STARTED")
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            **details: Additional event details as keyword arguments
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "component": self.component,
            "event_type": event_type,
            "level": level,
        }
        
        # Add league_id if available
        if self.league_id:
            entry["league_id"] = self.league_id
        
        # Add all additional details
        entry.update(details)
        
        # Write as single line JSON
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def debug(self, event_type: str, **details: Any) -> None:
        """Log a DEBUG level event."""
        self.log(event_type, level="DEBUG", **details)
    
    def info(self, event_type: str, **details: Any) -> None:
        """Log an INFO level event."""
        self.log(event_type, level="INFO", **details)
    
    def warning(self, event_type: str, **details: Any) -> None:
        """Log a WARNING level event."""
        self.log(event_type, level="WARNING", **details)
    
    def error(self, event_type: str, **details: Any) -> None:
        """Log an ERROR level event."""
        self.log(event_type, level="ERROR", **details)
    
    def log_message_sent(
        self,
        message_type: str,
        recipient: str,
        **details: Any,
    ) -> None:
        """
        Log a sent message.
        
        Args:
            message_type: Type of message (e.g., "GAME_START", "MOVE_REQUEST")
            recipient: Recipient ID
            **details: Additional message details
        """
        self.debug(
            "MESSAGE_SENT",
            message_type=message_type,
            recipient=recipient,
            **details,
        )
    
    def log_message_received(
        self,
        message_type: str,
        sender: str,
        **details: Any,
    ) -> None:
        """
        Log a received message.
        
        Args:
            message_type: Type of message
            sender: Sender ID
            **details: Additional message details
        """
        self.debug(
            "MESSAGE_RECEIVED",
            message_type=message_type,
            sender=sender,
            **details,
        )
