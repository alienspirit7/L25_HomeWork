"""Pydantic schemas for MCP protocol messages."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class PlayerMeta(BaseModel):
    """Player registration metadata."""
    display_name: str
    version: str = "1.0.0"
    game_types: List[str]
    contact_endpoint: str


class RegistrationResponse(BaseModel):
    """Response to player registration."""
    status: str  # ACCEPTED or REJECTED
    player_id: Optional[str] = None
    reason: Optional[str] = None


class GameInvitation(BaseModel):
    """GAME_INVITATION message."""
    protocol: str = "league.v1"
    message_type: str = "GAME_INVITATION"
    league_id: str
    round_id: int
    match_id: str
    conversation_id: str
    sender: str
    timestamp: str
    player_id: str
    game_type: str
    role_in_match: str  # PLAYER_A or PLAYER_B
    opponent_id: str


class GameJoinAck(BaseModel):
    """GAME_JOIN_ACK response."""
    protocol: str = "league.v1"
    message_type: str = "GAME_JOIN_ACK"
    league_id: str
    round_id: int
    match_id: str
    conversation_id: str
    sender: str
    timestamp: str
    player_id: str
    arrival_timestamp: str
    accept: bool = True


class ChooseParityCall(BaseModel):
    """CHOOSE_PARITY_CALL message."""
    protocol: str = "league.v1"
    message_type: str = "CHOOSE_PARITY_CALL"
    league_id: str
    round_id: int
    match_id: str
    conversation_id: str
    sender: str
    timestamp: str
    player_id: str
    game_type: str
    context: Dict
    deadline: str


class ChooseParityResponse(BaseModel):
    """CHOOSE_PARITY_RESPONSE message."""
    protocol: str = "league.v1"
    message_type: str = "CHOOSE_PARITY_RESPONSE"
    league_id: str
    round_id: int
    match_id: str
    conversation_id: str
    sender: str
    timestamp: str
    player_id: str
    parity_choice: str  # must be "even" or "odd"


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
    protocol: str = "league.v1"
    message_type: str = "GAME_OVER"
    league_id: str
    round_id: int
    match_id: str
    conversation_id: str
    sender: str
    timestamp: str
    game_type: str
    game_result: GameResult


class MatchResult(BaseModel):
    """Match result report to League Manager."""
    match_id: str
    winner: Optional[str]
    score: Dict[str, int]
    details: Dict


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
