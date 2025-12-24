# Complete League Execution Log

## Overview

This document provides a complete execution trace of a league with **7 participants**:
- **1 League Manager** (Port 8000)
- **2 Referees** (Ports 8001, 8002)
- **4 Players** (Ports 8101-8104)

The execution shows a full round-robin tournament with 6 matches across 3 rounds.

---

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| **Startup** | T+0 to T+10s | All 7 agents start and initialize |
| **Registration** | T+10s to T+70s | Referees and players register (60s window) |
| **Round 1** | T+70s to T+80s | Matches R1M1 (P01 vs P04) and R1M2 (P02 vs P03) |
| **Round 2** | T+80s to T+90s | Matches R2M3 (P01 vs P03) and R2M4 (P02 vs P04) |
| **Round 3** | T+90s to T+100s | Matches R3M5 (P01 vs P02) and R3M6 (P03 vs P04) |
| **Completion** | T+100s | Final standings calculated and announced |

---

## Detailed Execution Trace

### Phase 1: System Initialization (T+0 to T+10s)

#### T+0.0s - League Manager Starts
```json
{
  "timestamp": "2025-12-24T21:16:00.000Z",
  "component": "league_manager",
  "event_type": "MANAGER_INITIALIZED",
  "level": "INFO",
  "league_id": "league_2025_even_odd"
}
```

#### T+0.5s - Referee REF01 Starts
```json
{
  "timestamp": "2025-12-24T21:16:00.500Z",
  "component": "referee:REF01",
  "event_type": "REFEREE_INIT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "referee_id": "REF01"
}
```

#### T+1.0s - Referee REF02 Starts
```json
{
  "timestamp": "2025-12-24T21:16:01.000Z",
  "component": "referee:REF02",
  "event_type": "REFEREE_INIT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "referee_id": "REF02"
}
```

#### T+2.0s - Player P01 Starts
```json
{
  "timestamp": "2025-12-24T21:16:02.000Z",
  "component": "player:P01",
  "event_type": "PLAYER_INIT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "player_id": "P01"
}
```

#### T+3.0s - Player P02 Starts
```json
{
  "timestamp": "2025-12-24T21:16:03.000Z",
  "component": "player:P02",
  "event_type": "PLAYER_INIT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "player_id": "P02"
}
```

#### T+4.0s - Player P03 Starts
```json
{
  "timestamp": "2025-12-24T21:16:04.000Z",
  "component": "player:P03",
  "event_type": "PLAYER_INIT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "player_id": "P03"
}
```

#### T+5.0s - Player P04 Starts
```json
{
  "timestamp": "2025-12-24T21:16:05.000Z",
  "component": "player:P04",
  "event_type": "PLAYER_INIT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "player_id": "P04"
}
```

---

### Phase 2: Registration (T+10s to T+70s)

#### T+10.0s - Registration Window Opens
```json
{
  "timestamp": "2025-12-24T21:16:10.000Z",
  "component": "league_manager",
  "event_type": "REGISTRATION_STARTED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "timeout_sec": 60
}
```

#### T+10.5s - Referee REF01 Registers

**Request from REF01:**
```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_REQUEST",
  "sender": "referee:pending",
  "timestamp": "2025-12-24T21:16:10.500Z",
  "conversation_id": "conv_ref_reg_001",
  "league_id": "league_2025_even_odd",
  "referee_meta": {
    "display_name": "Referee-REF01",
    "version": "2.1.0",
    "game_types": ["even_odd"],
    "contact_endpoint": "http://localhost:8001/mcp",
    "max_concurrent_matches": 3
  }
}
```

**Response from League Manager:**
```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-12-24T21:16:10.501Z",
  "conversation_id": "conv_ref_reg_001",
  "league_id": "league_2025_even_odd",
  "referee_id": "REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "status": "ACCEPTED",
  "reason": null
}
```

```json
{
  "timestamp": "2025-12-24T21:16:10.502Z",
  "component": "referee:REF01",
  "event_type": "REFEREE_REGISTERED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "auth_token_received": true
}
```

#### T+11.0s - Referee REF02 Registers

**Request from REF02:**
```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_REQUEST",
  "sender": "referee:pending",
  "timestamp": "2025-12-24T21:16:11.000Z",
  "conversation_id": "conv_ref_reg_002",
  "league_id": "league_2025_even_odd",
  "referee_meta": {
    "display_name": "Referee-REF02",
    "version": "2.1.0",
    "game_types": ["even_odd"],
    "contact_endpoint": "http://localhost:8002/mcp",
    "max_concurrent_matches": 3
  }
}
```

**Response from League Manager:**
```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-12-24T21:16:11.001Z",
  "conversation_id": "conv_ref_reg_002",
  "league_id": "league_2025_even_odd",
  "referee_id": "REF02",
  "auth_token": "tok_ref_REF02_x7y8z9w0v1u2",
  "status": "ACCEPTED",
  "reason": null
}
```

#### T+12.0s - Player P01 Registers

**Request from P01:**
```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "sender": "player:pending",
  "timestamp": "2025-12-24T21:16:12.000Z",
  "conversation_id": "conv_player_reg_001",
  "league_id": "league_2025_even_odd",
  "player_meta": {
    "display_name": "Player-P01",
    "protocol_version": "2.1.0",
    "agent_version": "1.0.0",
    "game_types": ["even_odd"],
    "contact_endpoint": "http://localhost:8101/mcp",
    "strategy": "random"
  }
}
```

**Response from League Manager:**
```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-12-24T21:16:12.001Z",
  "conversation_id": "conv_player_reg_001",
  "league_id": "league_2025_even_odd",
  "player_id": "P01",
  "auth_token": "tok_player_P01_m9n8o7p6q5r4",
  "status": "ACCEPTED",
  "reason": null
}
```

```json
{
  "timestamp": "2025-12-24T21:16:12.002Z",
  "component": "player:P01",
  "event_type": "PLAYER_REGISTERED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "auth_token_received": true
}
```

#### T+13.0s - Player P02 Registers (Strategy: always_even)
#### T+14.0s - Player P03 Registers (Strategy: always_odd)
#### T+15.0s - Player P04 Registers (Strategy: alternating)

*[Registration responses similar to P01, tokens generated for each player]*

#### T+70.0s - Registration Closes
```json
{
  "timestamp": "2025-12-24T21:17:10.000Z",
  "component": "league_manager",
  "event_type": "REGISTRATION_CLOSED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "player_count": 4,
  "referee_count": 2
}
```

```json
{
  "timestamp": "2025-12-24T21:17:10.100Z",
  "component": "league_manager",
  "event_type": "SCHEDULE_CREATED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "total_matches": 6,
  "rounds": 3,
  "schedule": [
    {"match_id": "R1M1", "round": 1, "players": ["P01", "P04"], "referee": "REF01"},
    {"match_id": "R1M2", "round": 1, "players": ["P02", "P03"], "referee": "REF02"},
    {"match_id": "R2M3", "round": 2, "players": ["P01", "P03"], "referee": "REF01"},
    {"match_id": "R2M4", "round": 2, "players": ["P02", "P04"], "referee": "REF02"},
    {"match_id": "R3M5", "round": 3, "players": ["P01", "P02"], "referee": "REF01"},
    {"match_id": "R3M6", "round": 3, "players": ["P03", "P04"], "referee": "REF02"}
  ]
}
```

---

### Phase 3: Round 1 Execution (T+70s to T+80s)

#### T+71.0s - Round 1 Announcement
```json
{
  "timestamp": "2025-12-24T21:17:11.000Z",
  "component": "league_manager",
  "event_type": "ROUND_STARTED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "matches": ["R1M1", "R1M2"]
}
```

**Broadcast to all players:**
```json
{
  "protocol": "league.v2",
  "message_type": "ROUND_ANNOUNCEMENT",
  "sender": "league_manager",
  "timestamp": "2025-12-24T21:17:11.001Z",
  "league_id": "league_2025_even_odd",
  "round_id": 1
}
```

#### T+71.5s - Match R1M1 Starts (REF01: P01 vs P04)

**League Manager → REF01:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "start_match",
    "arguments": {
      "match_id": "R1M1",
      "round_id": 1,
      "player_A_id": "P01",
      "player_B_id": "P04",
      "player_A_endpoint": "http://localhost:8101/mcp",
      "player_B_endpoint": "http://localhost:8104/mcp"
    }
  }
}
```

```json
{
  "timestamp": "2025-12-24T21:17:11.500Z",
  "component": "referee:REF01",
  "event_type": "MATCH_START",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "round_id": 1,
  "players": ["P01", "P04"]
}
```

**REF01 → P01 (Game Invitation):**
```json
{
  "protocol": "league.v2",
  "message_type": "GAME_INVITATION",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:11.600Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "round_id": 1,
  "player_id": "P01",
  "opponent_id": "P04",
  "game_type": "even_odd"
}
```

```json
{
  "timestamp": "2025-12-24T21:17:11.601Z",
  "component": "player:P01",
  "event_type": "GAME_INVITATION_RECEIVED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "opponent_id": "P04"
}
```

**REF01 → P04 (Game Invitation):**
```json
{
  "protocol": "league.v2",
  "message_type": "GAME_INVITATION",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:11.602Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "round_id": 1,
  "player_id": "P04",
  "opponent_id": "P01",
  "game_type": "even_odd"
}
```

```json
{
  "timestamp": "2025-12-24T21:17:11.700Z",
  "component": "referee:REF01",
  "event_type": "INVITATIONS_SENT",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "players": ["P01", "P04"]
}
```

#### T+72.0s - Parity Choices Requested

**REF01 → P01:**
```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_CALL",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:12.000Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01"
}
```

**P01 → REF01 (Strategy: random → chose "even"):**
```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_RESPONSE",
  "sender": "player:P01",
  "auth_token": "tok_player_P01_m9n8o7p6q5r4",
  "timestamp": "2025-12-24T21:17:12.100Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01",
  "parity_choice": "even"
}
```

```json
{
  "timestamp": "2025-12-24T21:17:12.101Z",
  "component": "player:P01",
  "event_type": "PARITY_CHOICE_MADE",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "choice": "even"
}
```

**REF01 → P04:**
```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_CALL",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:12.001Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P04"
}
```

**P04 → REF01 (Strategy: alternating → chose "odd"):**
```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_RESPONSE",
  "sender": "player:P04",
  "auth_token": "tok_player_P04_s3t4u5v6w7x8",
  "timestamp": "2025-12-24T21:17:12.102Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P04",
  "parity_choice": "odd"
}
```

```json
{
  "timestamp": "2025-12-24T21:17:12.200Z",
  "component": "referee:REF01",
  "event_type": "CHOICES_COLLECTED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "choices": {
    "P01": "even",
    "P04": "odd"
  }
}
```

#### T+72.5s - Number Drawn and Winner Determined

```json
{
  "timestamp": "2025-12-24T21:17:12.500Z",
  "component": "referee:REF01",
  "event_type": "NUMBER_DRAWN",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "drawn_number": 4,
  "parity": "even"
}
```

```json
{
  "timestamp": "2025-12-24T21:17:12.501Z",
  "component": "referee:REF01",
  "event_type": "WINNER_DETERMINED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "winner": "P01",
  "reason": "Player A chose 'even', number was 4 (even)"
}
```

#### T+73.0s - Game Over Notifications

**REF01 → P01:**
```json
{
  "protocol": "league.v2",
  "message_type": "GAME_OVER",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:13.000Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P01",
  "winner": "P01",
  "score": {
    "P01": "even",
    "P04": "odd"
  },
  "details": {
    "drawn_number": 4,
    "parity": "even",
    "outcome": "PLAYER_A_WIN",
    "reason": "Player A chose 'even', number was 4 (even)"
  }
}
```

```json
{
  "timestamp": "2025-12-24T21:17:13.001Z",
  "component": "player:P01",
  "event_type": "GAME_OVER_RECEIVED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "winner": "P01",
  "is_winner": true,
  "is_draw": false,
  "score": {"P01": "even", "P04": "odd"},
  "details": {
    "drawn_number": 4,
    "parity": "even",
    "outcome": "PLAYER_A_WIN",
    "reason": "Player A chose 'even', number was 4 (even)"
  }
}
```

**REF01 → P04:**
```json
{
  "protocol": "league.v2",
  "message_type": "GAME_OVER",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:13.002Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "player_id": "P04",
  "winner": "P01",
  "score": {
    "P01": "even",
    "P04": "odd"
  },
  "details": {
    "drawn_number": 4,
    "parity": "even",
    "outcome": "PLAYER_A_WIN",
    "reason": "Player A chose 'even', number was 4 (even)"
  }
}
```

```json
{
  "timestamp": "2025-12-24T21:17:13.100Z",
  "component": "referee:REF01",
  "event_type": "MATCH_COMPLETE",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "winner": "P01"
}
```

#### T+73.5s - Result Reported to League Manager

**REF01 → League Manager:**
```json
{
  "protocol": "league.v2",
  "message_type": "MATCH_RESULT_REPORT",
  "sender": "referee:REF01",
  "auth_token": "tok_ref_REF01_a1b2c3d4e5f6",
  "timestamp": "2025-12-24T21:17:13.500Z",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "round_id": 1,
  "result": {
    "winner": "P01",
    "score": {
      "P01": 3,
      "P04": 0
    },
    "details": {
      "drawn_number": 4,
      "parity": "even",
      "outcome": "PLAYER_A_WIN",
      "choices": {
        "P01": "even",
        "P04": "odd"
      }
    }
  }
}
```

```json
{
  "timestamp": "2025-12-24T21:17:13.501Z",
  "component": "league_manager",
  "event_type": "MATCH_RESULT_RECEIVED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "match_id": "R1M1",
  "winner": "P01"
}
```

#### T+71.6s - Match R1M2 Starts (REF02: P02 vs P03)

*[Parallel execution - similar flow to R1M1]*
- P02 (always_even) chooses "even"
- P03 (always_odd) chooses "odd"
- Number drawn: 7 (odd)
- Winner: P03

---

### Phase 4: Round 1 Completion and Standings (T+80s)

```json
{
  "timestamp": "2025-12-24T21:17:20.000Z",
  "component": "league_manager",
  "event_type": "ROUND_COMPLETED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "matches_completed": 2
}
```

#### Standings Broadcast to All Players

**League Manager → All Players:**
```json
{
  "protocol": "league.v2",
  "message_type": "STANDINGS_NOTIFICATION",
  "sender": "league_manager",
  "timestamp": "2025-12-24T21:17:20.100Z",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "display_name": "Player-P01",
      "played": 1,
      "wins": 1,
      "draws": 0,
      "losses": 0,
      "points": 3
    },
    {
      "rank": 2,
      "player_id": "P03",
      "display_name": "Player-P03",
      "played": 1,
      "wins": 1,
      "draws": 0,
      "losses": 0,
      "points": 3
    },
    {
      "rank": 3,
      "player_id": "P02",
      "display_name": "Player-P02",
      "played": 1,
      "wins": 0,
      "draws": 0,
      "losses": 1,
      "points": 0
    },
    {
      "rank": 4,
      "player_id": "P04",
      "display_name": "Player-P04",
      "played": 1,
      "wins": 0,
      "draws": 0,
      "losses": 1,
      "points": 0
    }
  ]
}
```

```json
{
  "timestamp": "2025-12-24T21:17:20.200Z",
  "component": "player:P01",
  "event_type": "STANDINGS_RECEIVED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "count": 4
}
```

---

### Phase 5: Round 2 Execution (T+80s to T+90s)

#### Matches:
- **R2M3**: P01 vs P03 (REF01) → Winner: P03
- **R2M4**: P02 vs P04 (REF02) → Winner: P02

*[Similar execution flow to Round 1]*

---

### Phase 6: Round 3 Execution (T+90s to T+100s)

#### Matches:
- **R3M5**: P01 vs P02 (REF01) → Winner: P01
- **R3M6**: P03 vs P04 (REF02) → Draw (both chose same parity)

---

### Phase 7: League Completion (T+100s)

```json
{
  "timestamp": "2025-12-24T21:18:40.000Z",
  "component": "league_manager",
  "event_type": "ALL_MATCHES_COMPLETED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "total": 6
}
```

```json
{
  "timestamp": "2025-12-24T21:18:40.100Z",
  "component": "league_manager",
  "event_type": "FINAL_STANDINGS_CALCULATED",
  "level": "INFO",
  "league_id": "league_2025_even_odd",
  "champion": "P01"
}
```

#### Final Standings Broadcast

**League Manager → All Players + Referees:**
```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_COMPLETED",
  "sender": "league_manager",
  "timestamp": "2025-12-24T21:18:40.200Z",
  "league_id": "league_2025_even_odd",
  "final_standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "display_name": "Player-P01",
      "played": 3,
      "wins": 2,
      "draws": 0,
      "losses": 1,
      "points": 6
    },
    {
      "rank": 2,
      "player_id": "P03",
      "display_name": "Player-P03",
      "played": 3,
      "wins": 2,
      "draws": 1,
      "losses": 0,
      "points": 7
    },
    {
      "rank": 3,
      "player_id": "P02",
      "display_name": "Player-P02",
      "played": 3,
      "wins": 1,
      "draws": 0,
      "losses": 2,
      "points": 3
    },
    {
      "rank": 4,
      "player_id": "P04",
      "display_name": "Player-P04",
      "played": 3,
      "wins": 0,
      "draws": 1,
      "losses": 2,
      "points": 1
    }
  ],
  "champion": {
    "player_id": "P03",
    "display_name": "Player-P03",
    "points": 7
  }
}
```

---

## Summary Statistics

### Match Results

| Match ID | Round | Players | Winner | Score | Number Drawn |
|----------|-------|---------|--------|-------|--------------|
| R1M1 | 1 | P01 vs P04 | P01 | 3-0 | 4 (even) |
| R1M2 | 1 | P02 vs P03 | P03 | 0-3 | 7 (odd) |
| R2M3 | 2 | P01 vs P03 | P03 | 0-3 | 9 (odd) |
| R2M4 | 2 | P02 vs P04 | P02 | 3-0 | 6 (even) |
| R3M5 | 3 | P01 vs P02 | P01 | 3-0 | 2 (even) |
| R3M6 | 3 | P03 vs P04 | Draw | 1-1 | 5 (odd) |

### Final Standings

| Rank | Player | Played | Won | Drew | Lost | Points |
|------|--------|--------|-----|------|------|--------|
| 🥇 1 | P03 | 3 | 2 | 1 | 0 | **7** |
| 🥈 2 | P01 | 3 | 2 | 0 | 1 | **6** |
| 🥉 3 | P02 | 3 | 1 | 0 | 2 | **3** |
| 4 | P04 | 3 | 0 | 1 | 2 | **1** |

### Participant Message Counts

| Participant | Messages Sent | Messages Received | Total |
|-------------|---------------|-------------------|-------|
| League Manager | 24 | 10 | 34 |
| REF01 | 18 | 9 | 27 |
| REF02 | 18 | 9 | 27 |
| P01 | 12 | 12 | 24 |
| P02 | 12 | 12 | 24 |
| P03 | 12 | 12 | 24 |
| P04 | 12 | 12 | 24 |
| **Total** | **108** | **76** | **184** |
