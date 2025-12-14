"""Pydantic schemas for MCP protocol messages - League Protocol v2."""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from datetime import datetime


# ============================================================================
# Base Message Envelope
# ============================================================================

class MessageEnvelope(BaseModel):
    """Required fields in every message (Envelope)."""
    protocol: str = Field(default="league.v2", const=True)
    message_type: str
    sender: str  # Format: "player:P01" | "referee:REF01" | "league_manager"
    timestamp: str  # ISO-8601 UTC with Z suffix
    conversation_id: str
    auth_token: Optional[str] = None  # Required after registration
    league_id: Optional[str] = None
    round_id: Optional[int] = None
    match_id: Optional[str] = None

    @validator('timestamp')
    def validate_utc_timestamp(cls, v):
        """Ensure timestamp is UTC (ends with Z or +00:00)."""
        if not (v.endswith('Z') or v.endswith('+00:00')):
            raise ValueError('Timestamp must be UTC (end with Z or +00:00)')
        return v

    @validator('sender')
    def validate_sender_format(cls, v):
        """Validate sender format: player:ID, referee:ID, or league_manager."""
        if v == "league_manager":
            return v
        if ":" not in v:
            raise ValueError('Sender must be "league_manager" or "type:id"')
        agent_type, agent_id = v.split(":", 1)
        if agent_type not in ["player", "referee"]:
            raise ValueError('Agent type must be player or referee')
        if not agent_id:
            raise ValueError('Agent ID cannot be empty')
        return v


# ============================================================================
# Registration Messages
# ============================================================================

class RefereeMeta(BaseModel):
    """Referee registration metadata."""
    display_name: str
    version: str
    game_types: List[str]
    contact_endpoint: str
    max_concurrent_matches: int = 2


class RefereeRegisterRequest(BaseModel):
    """REFEREE_REGISTER_REQUEST message."""
    message_type: str = "REFEREE_REGISTER_REQUEST"
    referee_meta: RefereeMeta


class RefereeRegisterResponse(BaseModel):
    """REFEREE_REGISTER_RESPONSE message."""
    message_type: str = "REFEREE_REGISTER_RESPONSE"
    status: str  # ACCEPTED or REJECTED
    referee_id: Optional[str] = None
    auth_token: Optional[str] = None
    reason: Optional[str] = None


class PlayerMeta(BaseModel):
    """Player registration metadata."""
    display_name: str
    version: str = "1.0.0"
    protocol_version: str = "2.1.0"
    game_types: List[str]
    contact_endpoint: str


class LeagueRegisterRequest(BaseModel):
    """LEAGUE_REGISTER_REQUEST message."""
    message_type: str = "LEAGUE_REGISTER_REQUEST"
    player_meta: PlayerMeta


class LeagueRegisterResponse(BaseModel):
    """LEAGUE_REGISTER_RESPONSE message."""
    message_type: str = "LEAGUE_REGISTER_RESPONSE"
    status: str  # ACCEPTED or REJECTED
    player_id: Optional[str] = None
    auth_token: Optional[str] = None
    league_id: Optional[str] = None
    reason: Optional[str] = None


# Type aliases for convenience
RegistrationResponse = LeagueRegisterResponse


# ============================================================================
# Round Messages
# ============================================================================

class MatchAnnouncement(BaseModel):
    """Single match in round announcement."""
    match_id: str
    game_type: str
    player_A_id: str
    player_B_id: str
    referee_endpoint: str


class RoundAnnouncement(BaseModel):
    """ROUND_ANNOUNCEMENT message."""
    protocol: str = "league.v2"
    message_type: str = "ROUND_ANNOUNCEMENT"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    round_id: int
    matches: List[MatchAnnouncement]


class RoundCompleted(BaseModel):
    """ROUND_COMPLETED message."""
    protocol: str = "league.v2"
    message_type: str = "ROUND_COMPLETED"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    round_id: int
    matches_completed: int
    next_round_id: Optional[int] = None
    summary: Dict


# ============================================================================
# Game Messages
# ============================================================================

class GameInvitation(BaseModel):
    """GAME_INVITATION message."""
    protocol: str = "league.v2"
    message_type: str = "GAME_INVITATION"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str  # Required authentication token
    league_id: str
    round_id: int
    match_id: str
    game_type: str
    role_in_match: str  # PLAYER_A or PLAYER_B
    opponent_id: str


class GameJoinAck(BaseModel):
    """GAME_JOIN_ACK response."""
    protocol: str = "league.v2"
    message_type: str = "GAME_JOIN_ACK"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str  # Required authentication token
    league_id: str
    round_id: int
    match_id: str
    player_id: str
    arrival_timestamp: str
    accept: bool = True


class ChooseParityCall(BaseModel):
    """CHOOSE_PARITY_CALL message."""
    protocol: str = "league.v2"
    message_type: str = "CHOOSE_PARITY_CALL"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str  # Required authentication token
    league_id: str
    round_id: int
    match_id: str
    player_id: str
    game_type: str
    context: Dict
    deadline: str


class ChooseParityResponse(BaseModel):
    """CHOOSE_PARITY_RESPONSE message."""
    protocol: str = "league.v2"
    message_type: str = "CHOOSE_PARITY_RESPONSE"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str  # Required authentication token
    league_id: str
    round_id: int
    match_id: str
    player_id: str
    parity_choice: str  # must be "even" or "odd"

    @validator('parity_choice')
    def validate_parity(cls, v):
        """Ensure parity choice is lowercase even or odd."""
        if v not in ["even", "odd"]:
            raise ValueError('Parity choice must be "even" or "odd"')
        return v


# ============================================================================
# Result Messages
# ============================================================================

class GameResult(BaseModel):
    """Game result details."""
    status: str  # WIN, DRAW, or TECHNICAL_LOSS
    winner_player_id: Optional[str] = None
    drawn_number: int
    number_parity: str
    choices: Dict[str, str]
    reason: str


class GameOver(BaseModel):
    """GAME_OVER notification."""
    protocol: str = "league.v2"
    message_type: str = "GAME_OVER"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str  # Required authentication token
    league_id: str
    round_id: int
    match_id: str
    game_type: str
    game_result: GameResult


class MatchResultReport(BaseModel):
    """MATCH_RESULT_REPORT to League Manager."""
    protocol: str = "league.v2"
    message_type: str = "MATCH_RESULT_REPORT"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str
    league_id: str
    round_id: int
    match_id: str
    game_type: str
    result: Dict  # Contains winner, score, details


# ============================================================================
# Standings Messages
# ============================================================================

class StandingsEntry(BaseModel):
    """League standings entry."""
    rank: int
    player_id: str
    display_name: str
    played: int
    wins: int
    draws: int
    losses: int
    points: int


class LeagueStandingsUpdate(BaseModel):
    """LEAGUE_STANDINGS_UPDATE message."""
    protocol: str = "league.v2"
    message_type: str = "LEAGUE_STANDINGS_UPDATE"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    round_id: int
    standings: List[StandingsEntry]


# ============================================================================
# League Completion Messages
# ============================================================================

class LeagueCompleted(BaseModel):
    """LEAGUE_COMPLETED message."""
    protocol: str = "league.v2"
    message_type: str = "LEAGUE_COMPLETED"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    total_rounds: int
    total_matches: int
    champion: Dict  # {player_id, display_name, points}
    final_standings: List[Dict]


# ============================================================================
# Query Messages
# ============================================================================

class LeagueQuery(BaseModel):
    """LEAGUE_QUERY message."""
    protocol: str = "league.v2"
    message_type: str = "LEAGUE_QUERY"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str
    league_id: str
    query_type: str  # GET_STANDINGS, GET_SCHEDULE, GET_NEXT_MATCH, GET_PLAYER_STATS
    query_params: Dict


class LeagueQueryResponse(BaseModel):
    """LEAGUE_QUERY_RESPONSE message."""
    protocol: str = "league.v2"
    message_type: str = "LEAGUE_QUERY_RESPONSE"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    query_type: str
    success: bool
    data: Optional[Dict] = None
    error: Optional[Dict] = None


# ============================================================================
# Error Messages
# ============================================================================

class LeagueError(BaseModel):
    """LEAGUE_ERROR message."""
    protocol: str = "league.v2"
    message_type: str = "LEAGUE_ERROR"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    error_code: str  # E001, E003, E004, E005, E009, E011, E012, E018, E021
    error_description: str
    original_message_type: Optional[str] = None
    context: Optional[Dict] = None
    retryable: bool = False


class GameError(BaseModel):
    """GAME_ERROR message."""
    protocol: str = "league.v2"
    message_type: str = "GAME_ERROR"
    sender: str  # referee:REF01
    timestamp: str
    conversation_id: str
    match_id: str
    error_code: str
    error_description: str
    affected_player: str
    action_required: str
    retry_info: Optional[Dict] = None
    consequence: str
