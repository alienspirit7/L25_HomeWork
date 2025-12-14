# League Protocol V2 Specification

## Overview

League Protocol V2 is a JSON-RPC 2.0 based communication protocol for AI agent gaming leagues. It defines standardized message formats for league management, game refereeing, and player participation.

**Protocol Version:** `league.v2` (2.1.0)  
**MCP Version:** `v2024-11-05`  
**Transport:** HTTP POST to `/mcp` endpoint

---

## Core Principles

1. **UTC Timestamps**: All timestamps MUST be in ISO-8601 UTC format
2. **Authentication**: Auth tokens required for all post-registration messages
3. **Type Safety**: All messages validated using Pydantic schemas
4. **Error Handling**: Standardized error codes and retry policies

---

## Message Structure

### Base Envelope

All messages share a common envelope structure:

```json
{
  "protocol": "league.v2",
  "message_type": "<MESSAGE_TYPE>",
  "sender": "<sender_type>:<sender_id>",
  "timestamp": "2025-12-15T00:30:00Z",
  "conversation_id": "<unique_id>",
  "league_id": "<league_id>"
}
```

**Required Fields:**
- `protocol`: Must be `"league.v2"`
- `message_type`: One of the defined message types
- `sender`: Format: `{type}:{id}` (e.g., `player:P01`, `referee:REF01`)
- `timestamp`: ISO-8601 UTC timestamp
- `conversation_id`: Unique identifier for message thread
- `league_id`: League identifier

---

## Message Types

### 1. Registration Messages

#### REFEREE_REGISTER_REQUEST
Referees register with League Manager before matches begin.

```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_REQUEST",
  "sender": "referee:pending",
  "timestamp": "2025-12-15T00:30:00Z",
  "conversation_id": "conv_ref_001",
  "league_id": "league_2025_even_odd",
  "referee_meta": {
    "display_name": "Referee Alpha",
    "version": "2.0.0",
    "game_types": ["even_odd"],
    "contact_endpoint": "http://localhost:8001/mcp",
    "max_concurrent_matches": 2
  }
}
```

#### REFEREE_REGISTER_RESPONSE
League Manager responds with referee ID and auth token.

```json
{
  "message_type": "REFEREE_REGISTER_RESPONSE",
  "status": "ACCEPTED",
  "referee_id": "REF01",
  "auth_token": "tok_ref_REF01_abc123...",
  "reason": null
}
```

#### LEAGUE_REGISTER_REQUEST
Players register with League Manager.

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "sender": "player:pending",
  "timestamp": "2025-12-15T00:30:00Z",
  "conversation_id": "conv_player_001",
  "league_id": "league_2025_even_odd",
  "player_meta": {
    "display_name": "Alpha Bot",
    "protocol_version": "2.1.0",
    "agent_version": "1.0.0",
    "game_types": ["even_odd"],
    "contact_endpoint": "http://localhost:8101/mcp"
  }
}
```

#### LEAGUE_REGISTER_RESPONSE
League Manager responds with player ID and auth token.

```json
{
  "message_type": "LEAGUE_REGISTER_RESPONSE",
  "status": "ACCEPTED",
  "player_id": "P01",
  "auth_token": "tok_player_P01_xyz789...",
  "league_id": "league_2025_even_odd",
  "reason": null
}
```

### 2. Game Flow Messages

#### GAME_INVITATION
Referee invites player to a match.

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_INVITATION",
  "sender": "referee:REF01",
  "timestamp": "2025-12-15T00:35:00Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "round_id": 1,
  "player_id": "P01",
  "opponent_id": "P02",
  "game_type": "even_odd"
}
```

#### GAME_JOIN_ACK
Player acknowledges invitation.

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_JOIN_ACK",
  "sender": "player:P01",
  "timestamp": "2025-12-15T00:35:01Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01",
  "status": "READY"
}
```

#### CHOOSE_PARITY_CALL
Referee requests parity choice.

```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_CALL",
  "sender": "referee:REF01",
  "timestamp": "2025-12-15T00:35:05Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01"
}
```

#### CHOOSE_PARITY_RESPONSE
Player responds with choice.

```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_RESPONSE",
  "sender": "player:P01",
  "timestamp": "2025-12-15T00:35:06Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01",
  "parity_choice": "even"
}
```

#### GAME_OVER
Referee announces match result.

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_OVER",
  "sender": "referee:REF01",
  "timestamp": "2025-12-15T00:35:10Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01",
  "winner": "P01",
  "score": {
    "P01": "even",
    "P02": "odd"
  },
  "details": {
    "drawn_number": 4,
    "parity": "even",
    "outcome": "PLAYER_A_WIN"
  }
}
```

#### MATCH_RESULT_REPORT
Referee reports result to League Manager.

```json
{
  "protocol": "league.v2",
  "message_type": "MATCH_RESULT_REPORT",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_abc123...",
  "timestamp": "2025-12-15T00:35:15Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "round_id": 1,
  "result": {
    "winner": "P01",
    "score": {
      "P01": "even",
      "P02": "odd"
    },
    "details": {
      "drawn_number": 4,
      "parity": "even",
      "outcome": "PLAYER_A_WIN"
    }
  }
}
```

### 3. Query Messages

#### LEAGUE_QUERY
Players/Referees query League Manager.

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_QUERY",
  "sender": "player:P01",
  "auth_token": "tok_player_P01_xyz789...",
  "timestamp": "2025-12-15T00:40:00Z",
  "conversation_id": "conv_query_001",
  "league_id": "league_2025_even_odd",
  "query_type": "GET_STANDINGS",
  "query_params": {}
}
```

**Query Types:**
- `GET_STANDINGS` - Current league standings
- `GET_SCHEDULE` - Full match schedule
- `GET_NEXT_MATCH` - Player's next match (requires `player_id` in params)
- `GET_PLAYER_STATS` - Specific player stats (requires `player_id` in params)

#### LEAGUE_QUERY_RESPONSE
League Manager responds with query results.

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_QUERY_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-12-15T00:40:01Z",
  "conversation_id": "conv_query_001",
  "query_type": "GET_STANDINGS",
  "success": true,
  "data": {
    "standings": [
      {
        "rank": 1,
        "player_id": "P01",
        "display_name": "Alpha Bot",
        "played": 3,
        "wins": 2,
        "draws": 1,
        "losses": 0,
        "points": 7
      }
    ]
  }
}
```

### 4. Notification Messages

#### STANDINGS_NOTIFICATION
League Manager broadcasts standings after each round.

```json
{
  "protocol": "league.v2",
  "message_type": "STANDINGS_NOTIFICATION",
  "sender": "league_manager",
  "timestamp": "2025-12-15T00:45:00Z",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "display_name": "Alpha Bot",
      "points": 3,
      "wins": 1,
      "draws": 0,
      "losses": 0
    }
  ]
}
```

### 5. Error Messages

#### LEAGUE_ERROR
Standardized error response.

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_ERROR",
  "sender": "league_manager",
  "timestamp": "2025-12-15T00:50:00Z",
  "error_code": "E012",
  "error_message": "AUTH_TOKEN_INVALID",
  "original_message_type": "LEAGUE_QUERY",
  "context": {
    "sender": "player:P99"
  }
}
```

**Common Error Codes:**
- `E000` - Internal server error
- `E001` - Timeout
- `E003` - Missing required field
- `E005` - Player not registered
- `E009` - Connection failed
- `E012` - Invalid auth token
- `E018` - Registration closed / Protocol mismatch

---

## Authentication

All messages after registration MUST include `auth_token` field:

```json
{
  "auth_token": "tok_player_P01_xyz789...",
  ...
}
```

Token format: `tok_{type}_{id}_{random}`

---

## Retry Policy

**Retry these errors:**
- `E001` (Timeout): 3 retries, 2-second delay
- `E009` (Connection): 3 retries, 2-second delay

**Do NOT retry:**
- All other errors (immediate failure)

---

## Timeouts

- Registration window: 60 seconds (configurable)
- GAME_JOIN_ACK: 5 seconds
- CHOOSE_PARITY_RESPONSE: 30 seconds
- Timeout = Technical Loss

---

## Examples

See `doc/message-examples/` for complete message flow examples:
- Registration flow
- Match execution
- Error handling
