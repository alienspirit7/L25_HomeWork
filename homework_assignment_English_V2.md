# Homework Exercise: Even/Odd League

**© Dr. Yoram Segal - All Rights Reserved**

**Version 2.0**

**2025**

---

## Table of Contents

1. [Introduction: AI Agents and MCP Protocol](#1-introduction-ai-agents-and-mcp-protocol)
2. [General League Protocol](#2-general-league-protocol)
3. [Even/Odd Game](#3-evenodd-game)
4. [JSON Message Structures](#4-json-message-structures)
5. [Implementation Guide](#5-implementation-guide)
6. [Homework Exercise Requirements](#6-homework-exercise-requirements)
7. [Learning MCP Through the League Exercise](#7-learning-mcp-through-the-league-exercise)
8. [Running the League System](#8-running-the-league-system)
9. [League Data Protocol](#9-league-data-protocol)
10. [Python Toolkit](#10-python-toolkit)
11. [Project Structure](#11-project-structure)
12. [References](#12-references)

---

## 1. Introduction: AI Agents and MCP Protocol

### 1.1 What is an AI Agent?

An AI agent is autonomous software. The agent receives information from the environment. It processes the information. Then it performs actions.

An AI agent differs from a regular program. A regular program executes predetermined instructions. An AI agent decides on its own what to do. The decision is based on the current state.

#### 1.1.1 Characteristics of an AI Agent

Every AI agent has several characteristics:

- **Autonomy** - The agent operates independently.
- **Perception** - The agent perceives information from the environment.
- **Action** - The agent affects the environment.
- **Goal-orientation** - The agent has a defined goal.

In Dr. Yoram Segal's book "AI Agents with MCP" [1], it is explained how agents communicate. The book presents the MCP protocol in detail. We will use these principles in the exercise.

### 1.2 MCP Protocol – Model Context Protocol

MCP is a communication protocol. The protocol was developed by Anthropic. It enables AI agents to communicate with each other.

#### 1.2.1 Protocol Principles

The protocol is based on several principles:

1. **Structured Messages** - Every message is a JSON object.
2. **JSON-RPC 2.0 Standard** - The protocol uses this standard.
3. **Tools** - Agents expose functions as "tools".
4. **Flexible Transport** - Can use HTTP or stdio.

#### 1.2.2 Host/Server Architecture

In an MCP system, there are two types of components:

**MCP Server** - A component that provides services. The server exposes "tools" that can be called. Each tool is a function with defined parameters.

**Host (Orchestrator)** - A component that coordinates between servers. The host sends requests to servers. It receives responses and processes them.

```
                    Host
               (Orchestrator)
                    │
         ┌─────────┼─────────┐
         │         │         │
    JSON-RPC  JSON-RPC  JSON-RPC
         │         │         │
         ▼         ▼         ▼
    MCP Server 1  MCP Server 2  MCP Server 3
```

### 1.3 HTTP Transport on localhost

In this exercise, we will use HTTP transport. Each agent will operate on a different port on localhost.

#### 1.3.1 Port Definition

We will define fixed ports for each agent:

- **LeagueManager** - Port 8000
- **Referee** - Port 8001
- **Players** - Ports 8101 to 8104

Each agent implements a simple HTTP server. The server receives POST requests at the `/mcp` path. The request content is JSON-RPC 2.0.

#### 1.3.2 Example Agent Address

LeagueManager server address:
```
http://localhost:8000/mcp
```

First player server address:
```
http://localhost:8101/mcp
```

### 1.4 JSON-RPC Message Structure

Every message in the protocol is a JSON object. The message has a fixed structure.

**Basic Message Structure:**
```json
{
    "jsonrpc": "2.0",
    "method": "tool_name",
    "params": {
        "param1": "value1",
        "param2": "value2"
    },
    "id": 1
}
```

**Message Fields:**

- **jsonrpc** - Protocol version, always "2.0".
- **method** - The name of the tool to invoke.
- **params** - Parameters for the tool.
- **id** - Unique identifier for the request.

### 1.5 Exercise Objective

In this exercise, we will build a league system for AI agents. The system will include three types of agents:

1. **League Manager (LeagueManager)** - Manages the league, including registration of players and referees.
2. **Referee** - Registers with the league manager and manages individual games.
3. **Player Agents (PlayerAgents)** - Participate in games.

**Registration Process:** Before the league starts, both referees and players must register with the league manager. The league manager maintains a list of available referees and assigns them to games.

The specific game in the exercise is "Even/Odd". The general protocol allows replacing the game in the future. It will be possible to use Tic-Tac-Toe, 12 Questions, or other games.

#### 1.5.1 Learning Objective

At the end of the exercise, you will be able to:

- Understand the MCP protocol.
- Build a simple MCP server.
- Communicate between different agents.
- Run a full league in your environment.
- Ensure protocol compatibility with other students.

**Important:** All students will use the same protocol. This will allow your agents to play against each other in the future.

---

## 2. General League Protocol

### 2.1 Protocol Principles

The protocol defines uniform rules. The rules enable different agents to communicate. Every student can implement an agent in any language they want. As long as the agent respects the protocol - it will participate in the league.

#### 2.1.1 Separation into Three Layers

The system is composed of three layers:

1. **League Layer** - Tournament management, player registration, standings table.
2. **Judging Layer** - Single game management, move validation, winner announcement.
3. **Game Rules Layer** - Specific game logic (Even/Odd, Tic-Tac-Toe, etc.).

The separation is important. It allows replacing the game layer. The general protocol remains fixed.

### 2.2 Agent Types

#### 2.2.1 LeagueManager - League Manager

The league manager is a single agent. It is responsible for:

- Registering players to the league.
- Creating a schedule (Round-Robin).
- Receiving results from referees.
- Calculating and publishing standings table.

The league manager operates as an MCP server on port 8000.

#### 2.2.2 Referee

The referee manages a single game. **Important:** Before the referee can judge games, it must register with the league manager.

The referee is responsible for:

- Registration with the league manager - before the league starts.
- Inviting two players to a game.
- Managing game turns.
- Validating move legality.
- Announcing result and reporting to the league.

The referee operates as an MCP server on port 8001. There can be multiple referees in the system (ports 8001-8010).

#### 2.2.3 PlayerAgent - Player Agent

The player agent represents a player in the league. It is responsible for:

- Registering to the league.
- Receiving invitations to games.
- Choosing moves in the game.
- Updating internal state based on results.

Each player operates on a separate port (8101-8104).

### 2.3 Identifiers in the Protocol

Every component in the system is uniquely identified.

**Table 1: Identifiers in the League Protocol**

| Name | Type | Description |
|------|------|-------------|
| league_id | String | Unique league identifier |
| round_id | Integer | Round number in league |
| match_id | String | Single game identifier |
| game_type | String | Game type |
| player_id | String | Player identifier |
| referee_id | String | Referee identifier |
| conversation_id | String | Conversation identifier |

#### 2.3.1 Examples of Identifiers

- **league_id:** "league_2025_even_odd"
- **round_id:** 1, 2, 3, ...
- **match_id:** "R1M1" (Round 1 Match 1)
- **game_type:** "even_odd" or "tic_tac_toe"
- **player_id:** "P01", "P02", ..., "P20"
- **referee_id:** "REF01", "REF02", ...

### 2.4 Envelope - General Message Structure

Every message in the protocol must include an "Envelope" with fixed fields. The envelope ensures consistency and enables tracking of messages.

**Envelope - Message Envelope Structure:**
```json
{
    "protocol": "league.v2",
    "message_type": "GAME_INVITATION",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:30:00Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok_abc123def456...",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1"
}
```

#### 2.4.1 Required Fields in Envelope

**Table 2: Required Fields in Every Message**

| Field | Type | Description |
|-------|------|-------------|
| protocol | String | Protocol version, fixed "league.v2" |
| message_type | String | Message type (e.g., GAME_INVITATION) |
| sender | String | Sender identifier in type:id format |
| timestamp | String | ISO-8601 timestamp in UTC timezone |
| conversation_id | String | Unique conversation identifier |

#### 2.4.2 UTC/GMT Timezone Requirement

**Required:** All timestamps in the protocol must be in UTC/GMT timezone. This requirement ensures consistency between agents operating from different geographic locations.

**Table 3: Valid and Invalid Timestamp Formats**

| Format | Valid? | Explanation |
|--------|--------|-------------|
| 2025-01-15T10:30:00Z | ✓ | Z suffix indicates UTC |
| 2025-01-15T10:30:00+00:00 | ✓ | +00:00 offset equals UTC |
| 2025-01-15T10:30:00+02:00 | ✗ | Local timezone - forbidden |
| 2025-01-15T10:30:00 | ✗ | Without timezone - forbidden |

**Important Note:** An agent that sends a message with a non-UTC timezone will receive error E021 (INVALID_TIMESTAMP).

#### 2.4.3 Optional Fields

**Table 4: Optional Fields by Context**

| Field | Type | Description |
|-------|------|-------------|
| auth_token | String | Authentication token (required after registration) |
| league_id | String | League identifier |
| round_id | Integer | Round number |
| match_id | String | Game identifier |

#### 2.4.4 sender Field Format

The sender field identifies the message sender:

- **league_manager** - The league manager
- **referee:REF01** - Referee with identifier REF01
- **player:P01** - Player with identifier P01

#### 2.4.5 auth_token - Authentication Token

After successful registration, every agent receives an auth_token. The token must appear in every message sent after registration. This prevents impersonation of other agents.

**Receiving Token in Registration Response:**
```json
{
    "message_type": "LEAGUE_REGISTER_RESPONSE",
    "status": "ACCEPTED",
    "player_id": "P01",
    "auth_token": "tok_p01_abc123def456ghi789..."
}
```

### 2.5 General League Flow

#### 2.5.1 Stage 1: Referee Registration

In the first stage, each referee registers to the league. The referee sends a registration request to the league manager. The league manager assigns a referee_id and saves the referee's address.

```
Referee ──REFEREE_REGISTER_REQUEST──> LeagueManager
        <─REFEREE_REGISTER_RESPONSE──
```

#### 2.5.2 Stage 2: Player Registration

After referee registration, each player registers to the league. The player sends a registration request to the league manager. The league manager assigns a player_id and confirms.

```
PlayerAgent ──REGISTER_REQUEST──> LeagueManager
            <─REGISTER_RESPONSE──
```

#### 2.5.3 Stage 3: Schedule Creation

After all players have registered, the league manager creates a schedule. The schedule is based on the Round-Robin method.

#### 2.5.4 Stage 4: Round Announcement

Before each round, the league manager publishes a ROUND_ANNOUNCEMENT message. The message details all the games in the round. The league manager assigns a referee to each game from the list of registered referees.

#### 2.5.5 Stage 5: Game Management

The referee invites players to a game. It manages the game according to the game rules. At the end, it reports the result to the league manager.

#### 2.5.6 Stage 6: Standings Update

After each round, the league manager updates the standings table. It publishes the table to all players.

### 2.6 General Flow Diagram

```
        Start
          │
          ▼
   Register Referees
          │
          ▼
   Register Players
          │
          ▼
    Create Schedule
          │
          ▼
    ┌─────────────┐
    │ More        │ Yes
    │ Matches? ───────> Run Match
    └─────┬───────┘        │
          │ No             │
          ▼                │
   Update Standings <──────┘
          │
          ▼
         End
```

### 2.7 Timeouts - Response Times

For each message type, a maximum response time is defined. If the agent doesn't respond in time, the action is considered a failure.

**Table 5: Response Times by Message Type**

| Message Type | Timeout | Notes |
|--------------|---------|-------|
| REFEREE_REGISTER | 10sec | Referee registration to league |
| LEAGUE_REGISTER | 10sec | Player registration to league |
| GAME_JOIN_ACK | 5sec | Game arrival confirmation |
| CHOOSE_PARITY | 30sec | Even/Odd choice |
| GAME_OVER | 5sec | Game result receipt |
| MATCH_RESULT_REPORT | 10sec | Result report to league |
| LEAGUE_QUERY | 10sec | Information query |
| All others | 10sec | Default |

### 2.8 Agent Lifecycle

Each agent (player, referee) goes through defined states during the league.

#### 2.8.1 Agent States

- **INIT** - Agent started but not yet registered.
- **REGISTERED** - Agent successfully registered and received auth_token.
- **ACTIVE** - Agent is active and participating in games.
- **SUSPENDED** - Agent temporarily suspended (not responding).
- **SHUTDOWN** - Agent finished activity.

#### 2.8.2 State Transition Diagram

```
           register          league_start
    INIT ──────────> REGISTERED ──────────> ACTIVE
                                              │
                          error               │ timeout
                            │                 ▼
    SHUTDOWN <────────────────────────── SUSPENDED
           max_fail         recover
                              │
                              └──────────────┘
```

### 2.9 Error Handling

The protocol defines two types of error messages:

#### 2.9.1 LEAGUE_ERROR - League Error

The league manager sends this message when an error occurs at the league level.

**League Error Example:**
```json
{
    "protocol": "league.v2",
    "message_type": "LEAGUE_ERROR",
    "sender": "league_manager",
    "timestamp": "2025-01-15T10:35:00Z",
    "error_code": "E005",
    "error_name": "PLAYER_NOT_REGISTERED",
    "error_description": "Player ID not found in registry",
    "context": {
        "player_id": "P99"
    },
    "retryable": false
}
```

#### 2.9.2 GAME_ERROR - Game Error

The referee sends this message when an error occurs in a game.

**Game Error Example:**
```json
{
    "protocol": "league.v2",
    "message_type": "GAME_ERROR",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:31:00Z",
    "match_id": "R1M1",
    "player_id": "P01",
    "error_code": "E001",
    "error_name": "TIMEOUT_ERROR",
    "error_description": "Response not received within 30 seconds",
    "game_state": "COLLECTING_CHOICES",
    "retryable": true,
    "retry_count": 1,
    "max_retries": 3
}
```

#### 2.9.3 Common Error Codes

**Table 6: Main Error Codes**

| Code | Name | Description |
|------|------|-------------|
| E001 | TIMEOUT_ERROR | Response not received in time |
| E003 | MISSING_REQUIRED_FIELD | Required field missing |
| E004 | INVALID_PARITY_CHOICE | Invalid choice |
| E005 | PLAYER_NOT_REGISTERED | Player not registered |
| E009 | CONNECTION_ERROR | Connection failure |
| E011 | AUTH_TOKEN_MISSING | Authentication token missing |
| E012 | AUTH_TOKEN_INVALID | Invalid token |

#### 2.9.4 RetryPolicy - Retry Policy

Certain errors are retryable:

- **Maximum retries:** 3
- **Delay between retries:** 2 seconds
- **Retryable errors:** E001 (timeout), E009 (connection)
- After exhausting retries - Technical loss (TECHNICAL_LOSS).

### 2.10 Version Compatibility

#### 2.10.1 Version Declaration

During registration, each agent declares the protocol version it supports. The league manager checks compatibility before confirming registration.

**Version Declaration in Registration Request:**
```json
{
    "message_type": "LEAGUE_REGISTER_REQUEST",
    "player_meta": {
        "display_name": "Agent Alpha",
        "version": "1.0.0",
        "protocol_version": "2.1.0",
        "game_types": ["even_odd"]
    }
}
```

#### 2.10.2 Compatibility Policy

- **Current version:** 2.1.0
- **Minimum supported version:** 2.0.0
- Agents with older versions will receive error E018 (PROTOCOL_VERSION_MISMATCH).

### 2.11 Important Principles

#### 2.11.1 Single Source of Truth

The referee is the source of truth for game state. Players don't keep their own state. They rely on the information the referee sends.

#### 2.11.2 Communication Through Orchestrator

Players don't talk directly to each other. All communication goes through the referee or league manager. This ensures the protocol is maintained.

#### 2.11.3 Handling Failures

If a player doesn't respond:

1. The referee sends a GAME_ERROR message with retryable=true.
2. The player receives up to 3 attempts.
3. After exhausting attempts - Technical loss (TECHNICAL_LOSS).

---

## 3. Even/Odd Game

### 3.1 Game Description

The Even/Odd game is a simple game. It is suitable for demonstrating the league protocol.

#### 3.1.1 Game Rules

1. Two players participate in the game.
2. Each player chooses "even" or "odd".
3. The choices are made in parallel, without knowing the opponent's choice.
4. The referee draws a number between 1 and 10.
5. If the number is even - whoever chose "even" wins.
6. If the number is odd - whoever chose "odd" wins.
7. If both guessed wrong/right - it's a draw.

#### 3.1.2 Game Example

**Table 7: Example of Even/Odd Game**

| A's Choice | B's Choice | Number | Result |
|------------|------------|--------|--------|
| even | odd | 8 (even) | A wins |
| even | odd | 7 (odd) | B wins |
| odd | odd | 4 (even) | Draw |

### 3.2 Single Game Flow

#### 3.2.1 Stage 1: Game Invitation

The referee sends an invitation to both players. The invitation includes:

- Game identifier (match_id).
- Round identifier (round_id).
- Game type (game_type).

#### 3.2.2 Stage 2: Arrival Confirmation

Each player confirms receiving the invitation. The confirmation includes a timestamp.

#### 3.2.3 Stage 3: Collecting Choices

The referee contacts each player separately. It requests a choice: "even" or "odd". The player returns their choice.

**Important:** Players don't see the opponent's choice.

#### 3.2.4 Stage 4: Number Drawing

After receiving both choices, the referee draws a number. The number is between 1 and 10. The drawing must be random.

#### 3.2.5 Stage 5: Determining Winner

The referee checks:

- If the number is even and a player chose "even" - they win.
- If the number is odd and a player chose "odd" - they win.
- If both guessed wrong/right - it's a draw.

#### 3.2.6 Stage 6: Reporting Result

The referee sends:

1. GAME_OVER message to both players.
2. MATCH_RESULT_REPORT message to the league manager.

### 3.3 Game States

The game transitions between defined states:

```
WAITING          COLLECTING       DRAWING
FOR_PLAYERS ────> CHOICES ────────> NUMBER
  Both ACK         Both chose         │
                                      │ Result
                                      ▼
                                  FINISHED
```

#### 3.3.1 WAITING_FOR_PLAYERS State

The game starts in this state. The referee waits for players to confirm arrival. **Transition:** When both players sent GAME_JOIN_ACK.

#### 3.3.2 COLLECTING_CHOICES State

The referee collects choices from players. It calls each player's choose_parity. **Transition:** When both choices are received.

#### 3.3.3 DRAWING_NUMBER State

The referee draws a number and determines the winner. **Transition:** Automatic after calculation.

#### 3.3.4 FINISHED State

The game is complete. The result was reported.

### 3.4 Scoring System

#### 3.4.1 Game Scoring

**Table 8: Scoring Table**

| Result | Winner Points | Loser Points |
|--------|---------------|--------------|
| Win | 3 | 0 |
| Draw | 1 | 1 |
| Loss | 0 | 0 |

#### 3.4.2 League Standings

Standings are determined by:

1. Total points (descending).
2. Number of wins (descending).
3. Draw difference (descending).

### 3.5 Round-Robin League

In a league with 4 players, each player plays against everyone.

#### 3.5.1 Number of Games

For n players:
- Number of games in league: n(n-1)/2
- For 4 players: 4×3/2 = 6 games

#### 3.5.2 Sample Schedule

**Table 9: Schedule for 4 Players**

| Game | Player A | Player B |
|------|----------|----------|
| R1M1 | P01 | P02 |
| R1M2 | P03 | P04 |
| R2M1 | P01 | P03 |
| R2M2 | P02 | P04 |
| R3M1 | P01 | P04 |
| R3M2 | P02 | P03 |

### 3.6 Strategies for Players

#### 3.6.1 Random Strategy

The simplest approach. The player randomly chooses "even" or "odd". The chance to win is 50%.

**Random Strategy:**
```python
import random

def choose_parity_random():
    return random.choice(["even", "odd"])
```

#### 3.6.2 History-Based Strategy

The player remembers previous results. It tries to identify patterns in drawings.

**Note:** Since the drawing is random, this strategy won't improve long-term results.

#### 3.6.3 LLM-Guided Strategy

The player can use a language model. It builds a prompt and queries the model.

**Prompt Example:**
```python
prompt = """
You are playing Even/Odd game.
Choose "even" or "odd".
Previous results: even won 3 times, odd won 2 times.
Your choice (one word only):
"""
```

**Note:** Using an LLM is interesting but won't statistically improve performance. The game is a game of luck.

### 3.7 Game Rules Module

The rules module is a separate component in the referee. It defines the game-specific logic.

#### 3.7.1 Module Interface

The module provides functions:

- **init_game_state()** - Initialize game state.
- **validate_choice(choice)** - Validate choice legality.
- **draw_number()** - Draw a number.
- **determine_winner(choices, number)** - Determine winner.

#### 3.7.2 Separation Advantage

In the future, it's possible to replace the module. Instead of Even/Odd:

- Tic-Tac-Toe
- 21 Questions
- Memory game

Only the rules module changes. The general protocol remains identical.

### 3.8 Expansion for Additional Games

The protocol is designed to be general and not specific to the Even/Odd game. This section describes the generic layer that enables adding additional games.

#### 3.8.1 GAME_MOVE - Move Abstraction

CHOOSE_PARITY_CALL and CHOOSE_PARITY_RESPONSE messages are a specific case of a more general abstraction:

**Table 10: Mapping Specific to Generic Messages**

| Specific Message | Generic Message |
|------------------|-----------------|
| CHOOSE_PARITY_CALL | GAME_MOVE_CALL |
| CHOOSE_PARITY_RESPONSE | GAME_MOVE_RESPONSE |

#### 3.8.2 Generic Move Message Structure

**GAME_MOVE_CALL - Generic Move Request:**
```json
{
    "protocol": "league.v2",
    "message_type": "GAME_MOVE_CALL",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:30:15Z",
    "match_id": "R1M1",
    "player_id": "P01",
    "game_type": "even_odd",
    "move_request": {
        "move_type": "choose_parity",
        "valid_options": ["even", "odd"],
        "context": {}
    },
    "deadline": "2025-01-15T10:30:45Z"
}
```

**GAME_MOVE_RESPONSE - Generic Move Response:**
```json
{
    "protocol": "league.v2",
    "message_type": "GAME_MOVE_RESPONSE",
    "sender": "player:P01",
    "timestamp": "2025-01-15T10:30:20Z",
    "match_id": "R1M1",
    "player_id": "P01",
    "game_type": "even_odd",
    "move_data": {
        "move_type": "choose_parity",
        "choice": "even"
    }
}
```

#### 3.8.3 GameRegistry - Game Type Registration

The league manager maintains a registry of supported game types:

**Games Registry:**
```json
{
    "game_registry": {
        "even_odd": {
            "display_name": "Even/Odd",
            "move_types": ["choose_parity"],
            "valid_choices": {
                "choose_parity": ["even", "odd"]
            },
            "min_players": 2,
            "max_players": 2
        },
        "tic_tac_toe": {
            "display_name": "Tic-Tac-Toe",
            "move_types": ["place_mark"],
            "valid_choices": {
                "place_mark": ["0-8"]
            },
            "min_players": 2,
            "max_players": 2
        }
    }
}
```

#### 3.8.4 Abstraction Benefits

1. **Adding new games** - Without changing the basic protocol.
2. **Capability discovery** - A player can ask which games are supported.
3. **Unified validation** - The referee ensures the move is legal according to the schema.
4. **Forward compatibility** - Old agents can continue working with specific messages.

**Note:** In this exercise, we use the specific messages (CHOOSE_PARITY_*). The generic abstraction is presented for understanding the architecture.

---

## 4. JSON Message Structures

**Very Important:** This chapter defines all protocol messages. All students must use exactly these structures. This will allow your agents to communicate with each other.

### 4.1 Referee Registration to League Messages

#### 4.1.1 REFEREE_REGISTER_REQUEST - Referee Registration Request

- **From:** referee
- **To:** league_manager
- **Expected Response:** REFEREE_REGISTER_RESPONSE

A referee sends this request to the league manager before the league starts.

**Referee Registration Request to League:**
```json
{
    "message_type": "REFEREE_REGISTER_REQUEST",
    "referee_meta": {
        "display_name": "Referee Alpha",
        "version": "1.0.0",
        "game_types": ["even_odd"],
        "contact_endpoint": "http://localhost:8001/mcp",
        "max_concurrent_matches": 2
    }
}
```

**Required Fields:**

- **display_name** - Referee's display name.
- **version** - Referee's version.
- **game_types** - List of game types the referee can judge.
- **contact_endpoint** - Referee's server address.
- **max_concurrent_matches** - Maximum number of games the referee can manage in parallel.

#### 4.1.2 REFEREE_REGISTER_RESPONSE - Referee Registration Response

- **From:** league_manager
- **To:** referee (who sent the request)
- **Expected Response:** None (response message)

The league manager returns this response to the referee.

**Referee Registration Response to League:**
```json
{
    "message_type": "REFEREE_REGISTER_RESPONSE",
    "status": "ACCEPTED",
    "referee_id": "REF01",
    "reason": null
}
```

**Fields:**

- **status** - "ACCEPTED" or "REJECTED".
- **referee_id** - Identifier assigned to the referee (only if accepted).
- **reason** - Rejection reason (only if rejected).

### 4.2 Player Registration to League Messages

#### 4.2.1 LEAGUE_REGISTER_REQUEST - Player Registration Request

- **From:** player
- **To:** league_manager
- **Expected Response:** LEAGUE_REGISTER_RESPONSE

A player sends this request to the league manager.

**Registration Request to League:**
```json
{
    "message_type": "LEAGUE_REGISTER_REQUEST",
    "player_meta": {
        "display_name": "Agent Alpha",
        "version": "1.0.0",
        "game_types": ["even_odd"],
        "contact_endpoint": "http://localhost:8101/mcp"
    }
}
```

**Required Fields:**

- **display_name** - Player's display name.
- **version** - Agent's version.
- **game_types** - List of supported games.
- **contact_endpoint** - Player's server address.

#### 4.2.2 LEAGUE_REGISTER_RESPONSE - Registration Response

- **From:** league_manager
- **To:** player (who sent the request)
- **Expected Response:** None (response message)

The league manager returns this response.

**Registration Response to League:**
```json
{
    "message_type": "LEAGUE_REGISTER_RESPONSE",
    "status": "ACCEPTED",
    "player_id": "P01",
    "reason": null
}
```

**Fields:**

- **status** - "ACCEPTED" or "REJECTED".
- **player_id** - Identifier assigned to the player (only if accepted).
- **reason** - Rejection reason (only if rejected).

### 4.3 Round Messages

#### 4.3.1 ROUND_ANNOUNCEMENT - Round Announcement

- **From:** league_manager
- **To:** players (all registered players)
- **Expected Response:** None (broadcast message)

The league manager sends before each round.

**Round Announcement:**
```json
{
    "message_type": "ROUND_ANNOUNCEMENT",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "matches": [
        {
            "match_id": "R1M1",
            "game_type": "even_odd",
            "player_A_id": "P01",
            "player_B_id": "P02",
            "referee_endpoint": "http://localhost:8001/mcp"
        },
        {
            "match_id": "R1M2",
            "game_type": "even_odd",
            "player_A_id": "P03",
            "player_B_id": "P04",
            "referee_endpoint": "http://localhost:8001/mcp"
        }
    ]
}
```

### 4.4 Game Messages

#### 4.4.1 GAME_INVITATION - Game Invitation

- **From:** referee (managing the game)
- **To:** player (each of the two players in the game)
- **Expected Response:** GAME_JOIN_ACK

The referee sends to each player.

**Game Invitation:**
```json
{
    "message_type": "GAME_INVITATION",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1",
    "game_type": "even_odd",
    "role_in_match": "PLAYER_A",
    "opponent_id": "P02",
    "conversation_id": "conv-r1m1-001"
}
```

#### 4.4.2 GAME_JOIN_ACK - Arrival Confirmation

- **From:** player (who received invitation)
- **To:** referee (who sent the invitation)
- **Expected Response:** CHOOSE_PARITY_CALL (after all players confirm)

The player confirms receiving the invitation.

**Game Arrival Confirmation:**
```json
{
    "message_type": "GAME_JOIN_ACK",
    "match_id": "R1M1",
    "player_id": "P01",
    "arrival_timestamp": "2025-01-15T10:30:00Z",
    "accept": true
}
```

### 4.5 Even/Odd Game Choice Messages

#### 4.5.1 CHOOSE_PARITY_CALL - Choice Request

- **From:** referee
- **To:** player (each player in the game)
- **Expected Response:** CHOOSE_PARITY_RESPONSE

The referee requests the player to choose.

**Choice Request:**
```json
{
    "message_type": "CHOOSE_PARITY_CALL",
    "match_id": "R1M1",
    "player_id": "P01",
    "game_type": "even_odd",
    "context": {
        "opponent_id": "P02",
        "round_id": 1,
        "your_standings": {
            "wins": 2,
            "losses": 1,
            "draws": 0
        }
    },
    "deadline": "2025-01-15T10:30:30Z"
}
```

#### 4.5.2 CHOOSE_PARITY_RESPONSE - Choice Response

- **From:** player
- **To:** referee (who sent the request)
- **Expected Response:** GAME_OVER (after all players answer)

The player returns their choice.

**Choice Response:**
```json
{
    "message_type": "CHOOSE_PARITY_RESPONSE",
    "match_id": "R1M1",
    "player_id": "P01",
    "parity_choice": "even"
}
```

**Important:** The value of parity_choice must be exactly "even" or "odd".

### 4.6 Result Messages

#### 4.6.1 GAME_OVER - Game End

- **From:** referee
- **To:** players (both players in the game)
- **Expected Response:** None (update message)

The referee sends to both players.

**Game End Message:**
```json
{
    "message_type": "GAME_OVER",
    "match_id": "R1M1",
    "game_type": "even_odd",
    "game_result": {
        "status": "WIN",
        "winner_player_id": "P01",
        "drawn_number": 8,
        "number_parity": "even",
        "choices": {
            "P01": "even",
            "P02": "odd"
        },
        "reason": "P01 chose even, number was 8 (even)"
    }
}
```

**Possible values for status:**

- **"WIN"** - There is a winner.
- **"DRAW"** - Draw.
- **"TECHNICAL_LOSS"** - Technical loss (timeout, etc.).

#### 4.6.2 MATCH_RESULT_REPORT - Result Report to League

- **From:** referee (who managed the game)
- **To:** league_manager
- **Expected Response:** LEAGUE_STANDINGS_UPDATE (league manager broadcasts to all players)

The referee sends to the league manager.

**Result Report to League:**
```json
{
    "message_type": "MATCH_RESULT_REPORT",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1",
    "game_type": "even_odd",
    "result": {
        "winner": "P01",
        "score": {
            "P01": 3,
            "P02": 0
        },
        "details": {
            "drawn_number": 8,
            "choices": {
                "P01": "even",
                "P02": "odd"
            }
        }
    }
}
```

### 4.7 Standings Messages

#### 4.7.1 LEAGUE_STANDINGS_UPDATE - Standings Update

- **From:** league_manager
- **To:** players (all registered players)
- **Expected Response:** None (broadcast message)

The league manager sends to all players.

**Standings Table Update:**
```json
{
    "message_type": "LEAGUE_STANDINGS_UPDATE",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "standings": [
        {
            "rank": 1,
            "player_id": "P01",
            "display_name": "Agent Alpha",
            "played": 2,
            "wins": 2,
            "draws": 0,
            "losses": 0,
            "points": 6
        },
        {
            "rank": 2,
            "player_id": "P03",
            "display_name": "Agent Gamma",
            "played": 2,
            "wins": 1,
            "draws": 1,
            "losses": 0,
            "points": 4
        }
    ]
}
```

### 4.8 Round and League End Messages

#### 4.8.1 ROUND_COMPLETED - Round End

- **From:** league_manager
- **To:** players (all registered players)
- **Expected Response:** None (broadcast message)

The league manager sends this message to all participants at the end of a round.

**Round End Message:**
```json
{
    "protocol": "league.v2",
    "message_type": "ROUND_COMPLETED",
    "sender": "league_manager",
    "timestamp": "2025-01-15T12:00:00Z",
    "conversation_id": "conv-round1-complete",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "matches_completed": 2,
    "next_round_id": 2,
    "summary": {
        "total_matches": 2,
        "wins": 1,
        "draws": 1,
        "technical_losses": 0
    }
}
```

**Fields:**

- **round_id** - The round that ended.
- **matches_completed** - Number of games completed.
- **next_round_id** - The next round, or null if this is the last round.
- **summary** - Statistical summary of the round.

#### 4.8.2 LEAGUE_COMPLETED - League End

- **From:** league_manager
- **To:** all_agents (all agents - players and referees)
- **Expected Response:** None (final broadcast message)

The league manager sends this message to all agents at the end of the league.

**League End Message:**
```json
{
    "protocol": "league.v2",
    "message_type": "LEAGUE_COMPLETED",
    "sender": "league_manager",
    "timestamp": "2025-01-20T18:00:00Z",
    "conversation_id": "conv-league-complete",
    "league_id": "league_2025_even_odd",
    "total_rounds": 3,
    "total_matches": 6,
    "champion": {
        "player_id": "P01",
        "display_name": "Agent Alpha",
        "points": 9
    },
    "final_standings": [
        {"rank": 1, "player_id": "P01", "points": 9},
        {"rank": 2, "player_id": "P03", "points": 5},
        {"rank": 3, "player_id": "P02", "points": 3},
        {"rank": 4, "player_id": "P04", "points": 1}
    ]
}
```

**Fields:**

- **champion** - Champion details.
- **final_standings** - Final standings table.
- **total_rounds, total_matches** - League statistics.

### 4.9 Query Messages

#### 4.9.1 LEAGUE_QUERY - League Query

- **From:** player or referee
- **To:** league_manager
- **Expected Response:** LEAGUE_QUERY_RESPONSE

A player or referee sends a query to the league manager to receive information.

**Next Game Query:**
```json
{
    "protocol": "league.v2",
    "message_type": "LEAGUE_QUERY",
    "sender": "player:P01",
    "timestamp": "2025-01-15T14:00:00Z",
    "conversation_id": "conv-query-001",
    "auth_token": "tok_p01_abc123...",
    "league_id": "league_2025_even_odd",
    "query_type": "GET_NEXT_MATCH",
    "query_params": {
        "player_id": "P01"
    }
}
```

**Query Types (query_type):**

- **GET_STANDINGS** - Get standings table.
- **GET_SCHEDULE** - Get schedule.
- **GET_NEXT_MATCH** - Get next game details.
- **GET_PLAYER_STATS** - Get player statistics.

#### 4.9.2 LEAGUE_QUERY_RESPONSE - Query Response

- **From:** league_manager
- **To:** player or referee (original sender)
- **Expected Response:** None (response message)

The league manager returns a response to the query.

**Next Game Response:**
```json
{
    "protocol": "league.v2",
    "message_type": "LEAGUE_QUERY_RESPONSE",
    "sender": "league_manager",
    "timestamp": "2025-01-15T14:00:01Z",
    "conversation_id": "conv-query-001",
    "query_type": "GET_NEXT_MATCH",
    "success": true,
    "data": {
        "next_match": {
            "match_id": "R2M1",
            "round_id": 2,
            "opponent_id": "P03",
            "referee_endpoint": "http://localhost:8001/mcp"
        }
    }
}
```

**Fields:**

- **success** - Whether the query succeeded.
- **data** - Query result (structure changes according to query_type).
- **error** - Error details if success=false.

### 4.10 Error Messages

#### 4.10.1 LEAGUE_ERROR - League Level Error

- **From:** league_manager
- **To:** agent (the agent that caused the error)
- **Expected Response:** None (error message)

When an error occurs in league operations, the league manager sends a LEAGUE_ERROR message:

**LEAGUE_ERROR - League Error:**
```json
{
    "protocol": "league.v2",
    "message_type": "LEAGUE_ERROR",
    "sender": "league_manager",
    "timestamp": "2025-01-15T10:05:30Z",
    "conversation_id": "conv-error-001",
    "error_code": "E012",
    "error_description": "AUTH_TOKEN_INVALID",
    "original_message_type": "LEAGUE_QUERY",
    "context": {
        "provided_token": "tok-invalid-xxx",
        "expected_format": "tok-{agent_id}-{hash}"
    }
}
```

**Fields:**

- **error_code** - Error code from the error codes table.
- **error_description** - Error name.
- **original_message_type** - Message type that caused the error.
- **context** - Additional information for debugging.

#### 4.10.2 GAME_ERROR - Game Level Error

- **From:** referee (managing the game)
- **To:** player (the player who caused or is affected by the error)
- **Expected Response:** None (error message)

When an error occurs during a game, the referee sends a GAME_ERROR message:

**GAME_ERROR - Game Error:**
```json
{
    "protocol": "league.v2",
    "message_type": "GAME_ERROR",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:16:00Z",
    "conversation_id": "conv-r1m1-001",
    "match_id": "R1M1",
    "error_code": "E001",
    "error_description": "TIMEOUT_ERROR",
    "affected_player": "P02",
    "action_required": "CHOOSE_PARITY_RESPONSE",
    "retry_info": {
        "retry_count": 1,
        "max_retries": 3,
        "next_retry_at": "2025-01-15T10:16:02Z"
    },
    "consequence": "Technical loss if max retries exceeded"
}
```

**Fields:**

- **match_id** - Game identifier where the error occurred.
- **affected_player** - The affected player.
- **action_required** - The action that failed.
- **retry_info** - Information about retries (if relevant).
- **consequence** - Result if the error is not resolved.

### 4.11 Messages Summary Table

**Table 11: Summary of All 18 Message Types in Protocol v2.1**

| Message Type | Sender | Receiver | Purpose |
|--------------|--------|----------|---------|
| REFEREE_REGISTER_REQUEST | referee | league | Referee registration |
| REFEREE_REGISTER_RESPONSE | league | referee | Referee registration confirmation |
| LEAGUE_REGISTER_REQUEST | player | league | Player registration |
| LEAGUE_REGISTER_RESPONSE | league | player | Player registration confirmation |
| ROUND_ANNOUNCEMENT | league | players | Round publication |
| ROUND_COMPLETED | league | players | Round end |
| LEAGUE_COMPLETED | league | all | League end |
| GAME_INVITATION | referee | player | Game invitation |
| GAME_JOIN_ACK | player | referee | Arrival confirmation |
| CHOOSE_PARITY_CALL | referee | player | Choice request |
| CHOOSE_PARITY_RESPONSE | player | referee | Choice response |
| GAME_OVER | referee | players | Game end |
| MATCH_RESULT_REPORT | referee | league | Result report |
| LEAGUE_STANDINGS_UPDATE | league | players | Standings update |
| LEAGUE_ERROR | league | agent | League error |
| GAME_ERROR | referee | player | Game error |
| LEAGUE_QUERY | player/referee | league | Information query |
| LEAGUE_QUERY_RESPONSE | league | player/referee | Query response |

### 4.12 Important Rules

#### 4.12.1 Required Fields

Every message must include:

- **message_type** - Always.
- **match_id** - In game messages.
- **player_id** - In player messages.

#### 4.12.2 Allowed Values

- **parity_choice:** Only "even" or "odd" (lowercase).
- **status:** Only "WIN", "DRAW", or "TECHNICAL_LOSS".
- **accept:** Only true or false (boolean).

#### 4.12.3 Time Format

All timestamps in ISO-8601 format:
```
YYYY-MM-DDTHH:MM:SSZ
```
Example: 2025-01-15T10:30:00Z

---

## 5. Implementation Guide

This chapter presents how to implement the agents. The examples are in Python with FastAPI. You can use any language that supports HTTP.

### 5.1 General Architecture

#### 5.1.1 Components Diagram

```
              Orchestrator/Host
                    │
         ┌─────────┼─────────┐
         │         │         │
       HTTP      HTTP      HTTP
         │         │         │
         ▼         ▼         ▼
  LeagueManager  Referee   Players
     :8000       :8001    :8101-8104
```

#### 5.1.2 Orchestrator's Role

The Orchestrator coordinates between all agents. It:

- Sends HTTP requests to each server.
- Receives and processes responses.
- Manages the league flow.

### 5.2 Simple MCP Server Implementation

#### 5.2.1 Basic Structure in FastAPI

**Basic MCP Server:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: dict = {}
    id: int = 1

@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    if request.method == "tool_name":
        result = handle_tool(request.params)
        return MCPResponse(result=result, id=request.id)
    return MCPResponse(result={"error": "Unknown method"})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8101)
```

### 5.3 Player Agent Implementation

#### 5.3.1 Required Tools

A player agent must implement the following tools:

1. **handle_game_invitation** - Receive game invitation.
2. **choose_parity** - Choose "even" or "odd".
3. **notify_match_result** - Receive game result.

#### 5.3.2 Example Implementation

**Simple Player Agent:**
```python
import random
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1

@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    if request.method == "handle_game_invitation":
        return handle_invitation(request.params)
    elif request.method == "choose_parity":
        return handle_choose_parity(request.params)
    elif request.method == "notify_match_result":
        return handle_result(request.params)
    return {"error": "Unknown method"}

def handle_invitation(params):
    # Accept the invitation
    return {
        "message_type": "GAME_JOIN_ACK",
        "match_id": params.get("match_id"),
        "arrival_timestamp": datetime.now().isoformat(),
        "accept": True
    }

def handle_choose_parity(params):
    # Random strategy
    choice = random.choice(["even", "odd"])
    return {
        "message_type": "CHOOSE_PARITY_RESPONSE",
        "match_id": params.get("match_id"),
        "player_id": params.get("player_id"),
        "parity_choice": choice
    }

def handle_result(params):
    # Log result for learning
    print(f"Match result: {params}")
    return {"status": "ok"}
```

### 5.4 Referee Implementation

#### 5.4.1 Required Tools

The referee must implement:

1. **register_to_league** - Self-registration to league manager.
2. **start_match** - Start a new game.
3. **collect_choices** - Collect choices from players.
4. **draw_number** - Draw a number.
5. **finalize_match** - End game and report.

#### 5.4.2 Referee Registration to League

**Referee Registers to League Manager:**
```python
import requests

def register_to_league(league_endpoint, referee_info):
    payload = {
        "jsonrpc": "2.0",
        "method": "register_referee",
        "params": {
            "referee_meta": {
                "display_name": referee_info["name"],
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": referee_info["endpoint"],
                "max_concurrent_matches": 2
            }
        },
        "id": 1
    }
    response = requests.post(league_endpoint, json=payload)
    result = response.json()
    return result.get("result", {}).get("referee_id")
```

#### 5.4.3 Winner Determination Logic

**Determining Winner in Even/Odd Game:**
```python
def determine_winner(choice_a, choice_b, number):
    is_even = (number % 2 == 0)
    parity = "even" if is_even else "odd"
    
    a_correct = (choice_a == parity)
    b_correct = (choice_b == parity)
    
    if a_correct and not b_correct:
        return "PLAYER_A"
    elif b_correct and not a_correct:
        return "PLAYER_B"
    else:
        return "DRAW"
```

### 5.5 League Manager Implementation

#### 5.5.1 Required Tools

The league manager must implement:

1. **register_referee** - Register a new referee.
2. **register_player** - Register a new player.
3. **create_schedule** - Create schedule.
4. **report_match_result** - Receive result report.
5. **get_standings** - Return standings table.

#### 5.5.2 Referee Registration

**Referee Registration in League Manager:**
```python
class LeagueManager:
    def __init__(self):
        self.referees = {}  # referee_id -> referee_info
        self.players = {}   # player_id -> player_info
        self.next_referee_id = 1
    
    def register_referee(self, params):
        referee_meta = params.get("referee_meta", {})
        referee_id = f"REF{self.next_referee_id:02d}"
        self.next_referee_id += 1
        
        self.referees[referee_id] = {
            "referee_id": referee_id,
            "display_name": referee_meta.get("display_name"),
            "endpoint": referee_meta.get("contact_endpoint"),
            "game_types": referee_meta.get("game_types", []),
            "max_concurrent": referee_meta.get("max_concurrent_matches", 1)
        }
        
        return {
            "message_type": "REFEREE_REGISTER_RESPONSE",
            "status": "ACCEPTED",
            "referee_id": referee_id,
            "reason": None
        }
```

#### 5.5.3 Schedule Creation

**Round-Robin Algorithm:**
```python
from itertools import combinations

def create_schedule(players):
    matches = []
    round_num = 1
    match_num = 1
    
    for p1, p2 in combinations(players, 2):
        matches.append({
            "match_id": f"R{round_num}M{match_num}",
            "player_A_id": p1,
            "player_B_id": p2
        })
        match_num += 1
    
    return matches
```

### 5.6 Sending HTTP Requests

#### 5.6.1 Calling MCP Tool

**Sending Request to MCP Server:**
```python
import requests

def call_mcp_tool(endpoint, method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    response = requests.post(endpoint, json=payload)
    return response.json()

# Example: Call player's choose_parity
result = call_mcp_tool(
    "http://localhost:8101/mcp",
    "choose_parity",
    {"match_id": "R1M1", "player_id": "P01"}
)
```

### 5.7 State Management

#### 5.7.1 Player State

The player can keep internal information:

- Game history.
- Personal statistics.
- Information about opponents.

**Player State Class:**
```python
class PlayerState:
    def __init__(self, player_id):
        self.player_id = player_id
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.history = []
    
    def update(self, result):
        self.history.append(result)
        if result["winner"] == self.player_id:
            self.wins += 1
        elif result["winner"] == "DRAW":
            self.draws += 1
        else:
            self.losses += 1
```

### 5.8 Error Handling

#### 5.8.1 Response Time

**Request with Timeout:**
```python
import requests

def call_with_timeout(endpoint, method, params, timeout=30):
    try:
        response = requests.post(
            endpoint,
            json={"jsonrpc": "2.0", "method": method,
                  "params": params, "id": 1},
            timeout=timeout
        )
        return response.json()
    except requests.Timeout:
        return {"error": "TIMEOUT"}
    except requests.RequestException as e:
        return {"error": str(e)}
```

#### 5.8.2 Responding to Errors

If a player doesn't respond:

1. The referee waits until timeout.
2. If no response - technical loss.
3. The referee reports to the league manager.

### 5.9 Resilience Patterns

A distributed system must handle temporary failures. The protocol defines a retry policy:

- Maximum 3 retries.
- 2-second delay between retries.
- Exponential backoff recommended for loaded systems.

#### 5.9.1 Retry with Backoff Implementation

**Retry Logic:**
```python
import time
import requests
from typing import Optional, Dict, Any

class RetryConfig:
    MAX_RETRIES = 3
    BASE_DELAY = 2.0  # seconds
    BACKOFF_MULTIPLIER = 2.0

def call_with_retry(endpoint: str, method: str,
                    params: Dict[str, Any]) -> Dict[str, Any]:
    """Send MCP request with retry logic."""
    last_error = None
    
    for attempt in range(RetryConfig.MAX_RETRIES):
        try:
            response = requests.post(
                endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                },
                timeout=30
            )
            return response.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            last_error = e
            if attempt < RetryConfig.MAX_RETRIES - 1:
                delay = RetryConfig.BASE_DELAY * \
                        (RetryConfig.BACKOFF_MULTIPLIER ** attempt)
                time.sleep(delay)
    
    return {
        "error": {
            "error_code": "E005",
            "error_description": f"Max retries exceeded: {last_error}"
        }
    }
```

#### 5.9.2 CircuitBreaker Pattern

When a server fails multiple times, we avoid additional attempts for a certain period:

**Simple CircuitBreaker:**
```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if datetime.now() - self.last_failure > \
               timedelta(seconds=self.reset_timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN allows one try
    
    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = datetime.now()
        if self.failures >= self.threshold:
            self.state = "OPEN"
```

### 5.10 Structured Logging

The protocol requires JSON format logging for analysis and debugging. Each log message must include the following fields:

**Table 12: Required Fields in Log Message**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | ISO-8601 | Yes | Event time |
| level | string | Yes | DEBUG/INFO/WARN/ERROR |
| agent_id | string | Yes | Agent identifier |
| message_type | string | No | Message type |
| conversation_id | string | No | Conversation identifier |
| message | string | Yes | Event description |
| data | object | No | Additional data |

#### 5.10.1 Logger Implementation

**Structured Logger:**
```python
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any

class StructuredLogger:
    LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]
    
    def __init__(self, agent_id: str, min_level: str = "INFO"):
        self.agent_id = agent_id
        self.min_level = self.LEVELS.index(min_level)
    
    def log(self, level: str, message: str,
            message_type: Optional[str] = None,
            conversation_id: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None):
        
        if self.LEVELS.index(level) < self.min_level:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "agent_id": self.agent_id,
            "message": message
        }
        
        if message_type:
            log_entry["message_type"] = message_type
        if conversation_id:
            log_entry["conversation_id"] = conversation_id
        if data:
            log_entry["data"] = data
        
        print(json.dumps(log_entry), file=sys.stderr)
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)
```

#### 5.10.2 Usage Example

**Using Logger:**
```python
logger = StructuredLogger("player:P01")

# Log received message
logger.info(
    "Received game invitation",
    message_type="GAME_INVITATION",
    conversation_id="conv-12345",
    data={"match_id": "R1M1", "opponent": "P02"}
)

# Log error
logger.error(
    "Failed to connect to referee",
    data={"endpoint": "http://localhost:8001", "error": "timeout"}
)
```

**Log Output:**
```json
{"timestamp": "2025-01-15T10:30:00.123Z",
 "level": "INFO",
 "agent_id": "player:P01",
 "message": "Received game invitation",
 "message_type": "GAME_INVITATION",
 "conversation_id": "conv-12345",
 "data": {"match_id": "R1M1", "opponent": "P02"}}
```

### 5.11 Authentication and Tokens

Starting from protocol version 2.1.0, every message must include an auth_token for authentication. The token is received during registration and is used to identify the agent in every request.

#### 5.11.1 Receiving Token During Registration

**Registration and Receiving Token:**
```python
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentCredentials:
    agent_id: str
    auth_token: str
    league_id: str

def register_player(league_endpoint: str,
                    player_info: dict) -> Optional[AgentCredentials]:
    """Register player and store auth token."""
    payload = {
        "jsonrpc": "2.0",
        "method": "register_player",
        "params": {
            "protocol": "league.v2",
            "message_type": "LEAGUE_REGISTER_REQUEST",
            "sender": f"player:{player_info['name']}",
            "player_meta": player_info
        },
        "id": 1
    }
    
    response = requests.post(league_endpoint, json=payload)
    result = response.json().get("result", {})
    
    if result.get("status") == "ACCEPTED":
        return AgentCredentials(
            agent_id=result["player_id"],
            auth_token=result["auth_token"],
            league_id=result["league_id"]
        )
    return None
```

#### 5.11.2 Using Token in Requests

**Request with Authentication:**
```python
class AuthenticatedClient:
    def __init__(self, credentials: AgentCredentials):
        self.creds = credentials
    
    def send_message(self, endpoint: str, message_type: str,
                     params: dict) -> dict:
        """Send authenticated message."""
        payload = {
            "jsonrpc": "2.0",
            "method": "mcp_message",
            "params": {
                "protocol": "league.v2",
                "message_type": message_type,
                "sender": f"player:{self.creds.agent_id}",
                "auth_token": self.creds.auth_token,
                "league_id": self.creds.league_id,
                **params
            },
            "id": 1
        }
        
        response = requests.post(endpoint, json=payload)
        return response.json()
```

#### 5.11.3 Handling Authentication Errors

**Handling Authentication Errors:**
```python
def handle_auth_error(response: dict) -> bool:
    """Check for authentication errors."""
    error = response.get("error", {})
    error_code = error.get("error_code", "")
    
    if error_code == "E011":  # AUTH_TOKEN_MISSING
        print("Error: auth_token is required")
        return False
    elif error_code == "E012":  # AUTH_TOKEN_INVALID
        print("Error: auth_token is invalid or expired")
        # May need to re-register
        return False
    elif error_code == "E013":  # REFEREE_NOT_REGISTERED
        print("Error: Referee must register first")
        return False
    
    return True  # No auth error
```

### 5.12 Local Testing

#### 5.12.1 Local Execution

Run each agent in a separate terminal:

**Running Agents:**
```bash
# Terminal 1: League Manager (start first)
python league_manager.py  # Port 8000

# Terminal 2: Referee
python referee.py  # Port 8001

# Terminal 3-6: Players
python player.py --port 8101
python player.py --port 8102
python player.py --port 8103
python player.py --port 8104
```

**Important Execution Order:**

1. League manager must run first.
2. The referee registers to the league manager during startup.
3. Players register to the league manager.
4. Only then can the league start.

#### 5.12.2 Connection Testing

**Testing Server:**
```python
import requests

def test_server(port):
    try:
        r = requests.post(
            f"http://localhost:{port}/mcp",
            json={"jsonrpc": "2.0", "method": "ping", "id": 1}
        )
        print(f"Port {port}: OK")
    except:
        print(f"Port {port}: FAILED")

# Test all servers
for port in [8000, 8001, 8101, 8102, 8103, 8104]:
    test_server(port)
```

### 5.13 Implementation Tips

1. **Start simple** - First implement a random strategy.
2. **Test locally** - Run a league with your own code.
3. **Keep logs** - Document every message.
4. **Handle errors** - Use try/except.
5. **Follow the protocol** - Use JSON structures exactly.

---

## 6. Homework Exercise Requirements

### 6.1 Exercise Objective

In this exercise, you will implement a player agent for the Even/Odd league. At this stage, your agent will run only in your environment. It is recommended to coordinate with other students to ensure protocol compatibility.

**Very Important:** Use exactly the protocol defined in this document. Otherwise, your agent will not be able to communicate with others.

It is mandatory to plan and build the project in accordance with the guidelines of Chapter 9 (League Data Protocol), Chapter 10 (Python Toolkit), and Chapter 11 (Project Structure). Also ensure the project runs and functions as defined in Chapter 8 (Running the League System).

This exercise is based on the book:

**AI Agents with Model Context Protocol**
by Dr. Yoram Segal
December 9, 2025

It is highly recommended to read and study the subject in depth.

### 6.2 Required Tasks

#### 6.2.1 Task 1: Player Agent Implementation

Implement an MCP server that listens on a port on localhost. The server must support the following tools:

1. **handle_game_invitation** - Receive game invitation and return GAME_JOIN_ACK.
2. **choose_parity** - Choose "even" or "odd" and return CHOOSE_PARITY_RESPONSE.
3. **notify_match_result** - Receive game result and update internal state.

#### 6.2.2 Task 2: League Registration

The agent must send a registration request to the league manager. The request will include:

- A unique display name (your name or nickname).
- Agent version.
- The server's endpoint address.

#### 6.2.3 Task 3: Self-Testing

Before submission, test your agent:

1. Run a local league with 4 players.
2. Ensure the agent responds to every message type.
3. Ensure JSON structures match the protocol.

### 6.3 Technical Requirements

#### 6.3.1 Programming Language

You can choose any language you want. The important thing is that the agent:

- Implements an HTTP server.
- Responds to POST requests at the /mcp path.
- Returns JSON in JSON-RPC 2.0 format.

#### 6.3.2 Response Times

- **GAME_JOIN_ACK** - Within 5 seconds.
- **CHOOSE_PARITY_RESPONSE** - Within 30 seconds.
- **Any other response** - Within 10 seconds.

#### 6.3.3 Stability

The agent must:

- Operate without crashes.
- Handle input errors.
- Not stop operating mid-league.

### 6.4 Work Process

#### 6.4.1 Stage 1: Local Development

1. Implement the agent.
2. Test locally with your code.
3. Fix bugs.

#### 6.4.2 Stage 2: Private League

1. Run a local league with 4 copies of the agent.
2. Verify all communication works.
3. (Optional) Improve the strategy.

#### 6.4.3 Stage 3: Compatibility Testing with Other Students

1. Coordinate with another student for agent exchange.
2. Verify agents communicate properly with each other.
3. Ensure JSON structures match the protocol.

#### 6.4.4 Looking Forward: Class League

> **Important Note**
>
> In the future, you may be required to:
> - Create new games (not just Even/Odd).
> - Compete in a class league as part of the final course project.
>
> This topic is not yet closed and changes are possible. You should prepare for this and build the agent in a flexible way that allows future expansion.

### 6.5 Submission

#### 6.5.1 Files to Submit

1. Agent source code.
2. README file with running instructions.
3. A detailed report including:
   - Full description of the architecture and implementation.
   - Description of the chosen strategy and reasons for choosing it.
   - Difficulties encountered and their solutions.
   - Documentation of the development and testing process.
   - Conclusions from the exercise and recommendations for improvement.

#### 6.5.2 Submission Format

You should submit a link to a public repository. Submit using the regular submission procedure as submitted for previous exercises.

### 6.6 General Evaluation Criteria

Beyond the regular requirements, the following criteria will be evaluated:

**Table 13: Evaluation Criteria**

| Criterion | Description |
|-----------|-------------|
| Basic Functionality | Agent works, responds to messages, plays games |
| Protocol Compatibility | JSON structures match protocol exactly |
| Stability | Agent is stable, doesn't crash, handles errors |
| Code Quality | Clean, documented, organized code |
| Documentation | Clear running instructions, detailed description |
| Strategy | Implementation of interesting strategy (not just random) |

### 6.7 Frequently Asked Questions

#### 6.7.1 Can I use external libraries?

Yes. You can use any library you want. Make sure you provide installation instructions.

#### 6.7.2 Must I use Python?

No. Use any language that suits you. The important thing is that the agent meets the protocol requirements.

#### 6.7.3 What happens if my agent crashes?

The agent will suffer a technical loss in the current game. If it doesn't recover - it's out of the league.

#### 6.7.4 Can I update the agent after submission?

No. The submission is final. Test thoroughly before submitting.

#### 6.7.5 How will I know my ranking?

The standings table will be published after each round. You will be able to see your agent's position.

### 6.8 Summary

1. Implement a player agent that meets the protocol.
2. Test locally before submission.
3. Submit the code and report.
4. Your agent will play in the class league.

Good luck!

**Additional Information:**

- For questions and clarifications, contact Dr. Yoram Segal.
- It is recommended to read the book "AI Agents with MCP" [1].
- For more details on the MCP protocol, see the official documentation [2].

---

## 7. Learning MCP Through the League Exercise

The Even/Odd league exercise is not just a programming exercise. It constitutes an entire pedagogical model for understanding MCP protocol and AI agents principles. In this chapter, we will explain how the exercise teaches the foundational principles of AI agents and MCP protocol.

### 7.1 The Player as an AI Agent

#### 7.1.1 Is the Player Agent an AI Agent?

The first question to ask is: Is the PlayerAgent in the league really an AI agent? The answer is unequivocally: Yes.

An AI agent is defined as an entity that maintains interaction with the environment to achieve defined goals [1]. Unlike a regular program that executes predetermined instructions, an AI agent is autonomous software that receives information from the environment, processes it, and decides on its own what action to perform based on the current state.

#### 7.1.2 The Four Characteristics of an AI Agent

Let's examine the player agent in the league in light of the four main characteristics of an AI agent:

1. **Autonomy** - In the game context, the player agent autonomously decides which strategy to choose: "even" or "odd". No one tells it what to choose.

2. **Perception** - The player perceives information from the environment. It receives game invitation messages (GAME_INVITATION), parity choice requests (CHOOSE_PARITY_CALL), and game results (GAME_OVER) from the referee and league manager.

3. **Action** - The player performs actions that affect the environment by sending choices (CHOOSE_PARITY_RESPONSE) and arrival confirmations (GAME_JOIN_ACK) to games.

4. **Goal-orientation** - It has a defined goal. Its goal is to play, win games, and update its internal state, such as wins and losses history.

The player agent can even use a Large Language Model (LLM) to choose the best strategy. In doing so, it demonstrates "thinking" or "inference" before action execution.

### 7.2 The Player in MCP Architecture

#### 7.2.1 Server or Client?

The player, in the Even/Odd league architecture, is essentially an MCP Server.

An MCP server is the component that exposes services and capabilities, called "Tools", "Resources", or "Prompts". The server is defined as a separate process running on a defined port and provides a "gate" to the external world [2].

The player agent is required to implement an HTTP server that receives POST requests at the /mcp path. The tools it exposes are called via JSON-RPC 2.0 protocol. The tools the player must implement include:

- **handle_game_invitation** - Handling game invitation.
- **choose_parity** - Choosing "even" or "odd".
- **notify_match_result** - Receiving notification about game result.

#### 7.2.2 Relationships with the Referee and League Manager

Given that the player is a server, whoever calls its services acts as a Client. In the league system, the referee and league manager act as clients or Orchestrators.

The referee creates the JSON-RPC request that calls the player's choose_parity tool. When the referee wants to collect choices from players, it sends a CHOOSE_PARITY_CALL request to each player.

**Summary:** Although the player agent is an autonomous AI agent, from an MCP protocol implementation perspective, it fills the role of a server offering capabilities to the central orchestrators.

### 7.3 The Referee and League Manager as AI Agents

#### 7.3.1 Higher-Level Agents

The referee and league manager are also defined as AI agents. They also meet the same four characteristics:

**Table 14: AI Agent Characteristics for Referee and League Manager**

| Characteristic | League Manager | Referee |
|----------------|----------------|---------|
| Goal-orientation | Managing entire league, registration of referees and players, schedule creation, standings calculation | Registering to league manager, managing single game, validating move legality, determining winner |
| Autonomy | Operates independently for referee and player registration, game rounds | Registers independently to league, manages game stages |
| Perception | Receives registration requests from players and referees, receives result reports from referees | Receives arrival confirmations, parity choices from players |
| Action | Confirms referee and player registration, sends round announcements, updates standings tables | Sends registration request to league, sends invitations, choice requests, reports results |

These agents are not passive. They manage the entire system according to rules and goals. This is the essence of autonomy and goal-orientation of an AI agent.

#### 7.3.2 MCP Servers That Also Act as Clients

Both these agents are defined as MCP servers:

- The league manager operates as an MCP server on port 8000. It implements tools like register_referee, register_player, report_match_result.
- The referee operates as an MCP server on port 8001. It implements tools like start_match, collect_choices.

**Important Note:** Both these agents, although defined as servers, must also act as MCP clients to fulfill their central role. For example:

- The referee must act as a client to register with the league manager (REFEREE_REGISTER_REQUEST).
- The referee must act as a client to call the player's choose_parity tool - it calls the player servers and thus triggers the autonomous action of the player.
- The league manager must act as a client to send round announcements to the player agents.

In this system, the central servers are actually client-orchestrators when they need to trigger action at the player servers.

### 7.4 Central Insight: Role Reversal

#### 7.4.1 The Traditional Paradigm

In typical client-server architecture, the client is the active component that sends requests, and the server is the passive component that waits for requests.

#### 7.4.2 Role Reversal in the League

A creative role reversal exists in the AI league:

**The Player (autonomous agent) is the server:** Although the player is the autonomous entity that needs to perform action, it is required to expose its capabilities as an MCP server.

**The Referee and League Manager (orchestrators) are the clients:** The referee is the orchestrator that acts as an MCP client and calls the player's choose_parity tool to drive the next move in the game.

```
    Player 1          Player 2
  (MCP Server)     (MCP Server)
     :8101            :8102
        │                │
 choose_parity    choose_parity
        │                │
        └────────┬───────┘
                 │
      Referee (Orchestrator)
      Acts as MCP Client
           :8001
                 │
    ROUND_ANNOUNCEMENT
                 │
         League Manager
        Acts as MCP Client
             :8000
```

### 7.5 Layer Separation Principle

#### 7.5.1 Three Separate Layers

MCP protocol enables clear separation between roles:

1. **League Layer** (managed by league manager) - Player recruitment, schedule (Round-Robin), and standings table.
2. **Judging Layer** (managed by referee) - Single game management and move validation.
3. **Game Rules Layer** (managed by separate module) - Game-specific logic for Even/Odd.

#### 7.5.2 Separation Advantage

The player, by exposing a standard MCP interface (JSON-RPC 2.0 over HTTP), allows the league to remain agnostic to the development language or internal strategy.

This is a solution to the fragmentation problem where each agent and each model previously required unique integration. MCP protocol solves this by creating a universal interface [2].

When the player receives a request like CHOOSE_PARITY_CALL, the data arrives in a fixed JSON structure. The player responds, also in a fixed structure, with CHOOSE_PARITY_RESPONSE. This ensures that any agent, regardless of how it computes the data, can consistently communicate with any other orchestrator that respects the protocol.

### 7.6 The LLM's Role in the Server Agent

#### 7.6.1 The Dilemma

An interesting question arises: On one hand, the player is defined as an MCP server that exposes capabilities. On the other hand, it is described as an autonomous AI agent that can use an LLM as a "brain" for strategy choice. In traditional definitions, a server doesn't activate a "brain" but rather fulfills requests.

#### 7.6.2 The Solution: Role Separation

The solution lies in understanding that MCP roles (server/client) and AI components (brain/tools) are separate but complementary concepts.

**The agent is both a server and a client (in practice):** For each agent, the server role is required to host the agent allowing other agents to call its tools. The client role is required for any agent that needs to initiate interaction.

**The LLM as an internal component:** If the player agent implements an LLM-guided strategy, the LLM is simply an internal component within the agent loop. When the server receives a choose_parity request:

1. The MCP layer (server) receives the request.
2. The agent's internal logic (LLM or other strategy) is activated to determine the choice.
3. The MCP layer (server) sends back the response.

The LLM is the server's "intelligence". The central idea in MCP is to ensure that when a "brain" is inside the server, external communication remains standard via JSON-RPC.

#### 7.6.3 Analogy: Customer Service Station

The architecture can be imagined as a customer service station:

- **MCP (protocol)** - The telephone and the language spoken.
- **Player (server)** - The service office with its own phone line.
- **LLM/Strategy (brain)** - The smart advisor sitting inside the office, receiving the call, computing the answer, and dictating to the MCP layer what response to send back.

The internal tools (LLM and logic) are not directly exposed to MCP protocol, but rather serve the public tools the agent exposes, such as choose_parity.

### 7.7 The Orchestrator's Role

#### 7.7.1 League Manager - The Architect

The league manager is the AI agent at the highest level strategically, managing the league layer. It is not involved in the game rules themselves, but rather in general management: schedule and standings table.

**Separation Advantage:** If a league wants to replace the game from Even/Odd to Tic-Tac-Toe, the league manager changes hardly at all. This is a perfect demonstration of the role separation principle promoted by MCP.

#### 7.7.2 The Referee - The Dynamic Implementer

The referee embodies the judging layer. It doesn't know the game rules (handled by a separate module). Rather, it is responsible for Conversation Lifecycle management between players.

The referee ensures players meet response deadlines. It activates the external agent loop for players - it calls their choose_parity tool and thereby triggers the player's autonomous action.

MCP enables the clear role division: The referee and league manager are responsible for the "how" (protocol and communication), while the players are responsible for the "what" (content and strategy).

### 7.8 What the Exercise Teaches

#### 7.8.1 AI Agents Foundational Principles

The exercise teaches practically the four characteristics of an AI agent:

- **Autonomy** - The player decides on its own.
- **Perception** - The player perceives messages from the system.
- **Action** - The player sends responses.
- **Goal-orientation** - The player aspires to win.

#### 7.8.2 MCP Foundational Principles

The exercise teaches core MCP protocol principles:

1. **Standard Interface** - Each agent exposes tools via JSON-RPC 2.0.
2. **Role Separation** - League layer, judging layer, and game rules layer.
3. **Language Agnosticism** - An agent can be implemented in any programming language.
4. **Communication Through Orchestrator** - Agents don't talk directly, but rather through the referee or league manager.
5. **Agent Registration** - Both referees and players register with the league manager before games begin.

#### 7.8.3 The Learning Experience

At the exercise's conclusion, the student will understand:

- How an AI agent communicates with other agents.
- How to build a simple MCP server.
- What "Tools" mean in MCP protocol.
- How an orchestrator manages interaction between agents.
- Why layer separation is important for AI system design.

### 7.9 Summary

The Even/Odd league exercise constitutes a perfect pedagogical model for understanding MCP protocol and AI agents. The simple game allows focusing on architectural principles without getting entangled in complex logic.

The student learns that an AI agent can also be an MCP server - a creative role reversal that allows the orchestrator to call and trigger action at the agents. Layer separation ensures that the league game can be replaced in the future without changing the general protocol.

For more details on MCP protocol, see the book "AI Agents with MCP" [1] and Anthropic's official documentation [2].

---

## 8. Running the League System

This appendix presents practical guidance for running the full league system. We will demonstrate how to activate all the agents and manage a league with one league manager, two referees, and four players. The examples are based on the league.v2 protocol described in previous chapters.

### 8.1 System Configuration

#### 8.1.1 Terminals and Ports

Each agent in the system operates as a separate HTTP server on a dedicated port on localhost. In this example, we will run 7 terminals:

**Table 15: Port and Terminal Allocation**

| Endpoint | Port | Agent | Terminal |
|----------|------|-------|----------|
| http://localhost:8000/mcp | 8000 | League Manager | 1 |
| http://localhost:8001/mcp | 8001 | Referee REF01 | 2 |
| http://localhost:8002/mcp | 8002 | Referee REF02 | 3 |
| http://localhost:8101/mcp | 8101 | Player P01 | 4 |
| http://localhost:8102/mcp | 8102 | Player P02 | 5 |
| http://localhost:8103/mcp | 8103 | Player P03 | 6 |
| http://localhost:8104/mcp | 8104 | Player P04 | 7 |

#### 8.1.2 Orchestrator Roles

There are two types of Orchestrators in the system:

- **League Manager** - Supreme Orchestrator of the league. It is the source of truth for the standings table, schedule, and round status.
- **Referees** - Local Orchestrators for individual games. Each referee is the source of truth for their game's state.

### 8.2 Startup Order

#### 8.2.1 Startup Order Principle

The startup order is critical for proper system functioning:

1. **League Manager** - Must come up first.
2. **Referees** - Come up and register with the league manager.
3. **Players** - Come up and register with the league manager.
4. **League Start** - Only after all registrations complete.

#### 8.2.2 Terminal 1 - League Manager

**Starting League Manager:**
```bash
# Terminal 1 - League Manager
python league_manager.py  # Listening on :8000
```

The league manager listens for POST requests at http://localhost:8000/mcp.

#### 8.2.3 Terminals 2-3 - Referees

**Starting Referees:**
```bash
# Terminal 2 - Referee Alpha
python referee.py --port 8001

# Terminal 3 - Referee Beta
python referee.py --port 8002
```

Each referee, during startup, activates a register_to_league function that sends REFEREE_REGISTER_REQUEST to the league manager.

#### 8.2.4 Terminals 4-7 - Players

**Starting Players:**
```bash
# Terminal 4 - Player P01
python player.py --port 8101

# Terminal 5 - Player P02
python player.py --port 8102

# Terminal 6 - Player P03
python player.py --port 8103

# Terminal 7 - Player P04
python player.py --port 8104
```

Each player sends LEAGUE_REGISTER_REQUEST to the league manager.

### 8.3 Stage 1: Referee Registration

Each referee, immediately with its server startup, calls from the client side to the league manager.

#### 8.3.1 Referee Registration Request

**REFEREE_REGISTER_REQUEST - Referee Registration Request:**
```json
{
    "jsonrpc": "2.0",
    "method": "register_referee",
    "params": {
        "protocol": "league.v2",
        "message_type": "REFEREE_REGISTER_REQUEST",
        "sender": "referee:alpha",
        "timestamp": "2025-01-15T10:00:00Z",
        "conversation_id": "conv-ref-alpha-reg-001",
        "referee_meta": {
            "display_name": "Referee Alpha",
            "version": "1.0.0",
            "game_types": ["even_odd"],
            "contact_endpoint": "http://localhost:8001/mcp",
            "max_concurrent_matches": 2
        }
    },
    "id": 1
}
```

#### 8.3.2 League Manager Response

**REFEREE_REGISTER_RESPONSE - Referee Registration Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "REFEREE_REGISTER_RESPONSE",
        "sender": "league_manager",
        "timestamp": "2025-01-15T10:00:01Z",
        "conversation_id": "conv-ref-alpha-reg-001",
        "status": "ACCEPTED",
        "referee_id": "REF01",
        "auth_token": "tok-ref01-abc123",
        "league_id": "league_2025_even_odd",
        "reason": null
    },
    "id": 1
}
```

The second referee (on port 8002) sends a similar request and receives referee_id: "REF02".

### 8.4 Stage 2: Player Registration

After referees registered, each player sends a registration request.

#### 8.4.1 Player Registration Request

**LEAGUE_REGISTER_REQUEST - Player Registration Request:**
```json
{
    "jsonrpc": "2.0",
    "method": "register_player",
    "params": {
        "protocol": "league.v2",
        "message_type": "LEAGUE_REGISTER_REQUEST",
        "sender": "player:alpha",
        "timestamp": "2025-01-15T10:05:00Z",
        "conversation_id": "conv-player-alpha-reg-001",
        "player_meta": {
            "display_name": "Agent Alpha",
            "version": "1.0.0",
            "game_types": ["even_odd"],
            "contact_endpoint": "http://localhost:8101/mcp"
        }
    },
    "id": 1
}
```

#### 8.4.2 League Manager Response

**LEAGUE_REGISTER_RESPONSE - Player Registration Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "LEAGUE_REGISTER_RESPONSE",
        "sender": "league_manager",
        "timestamp": "2025-01-15T10:05:01Z",
        "conversation_id": "conv-player-alpha-reg-001",
        "status": "ACCEPTED",
        "player_id": "P01",
        "auth_token": "tok-p01-xyz789",
        "league_id": "league_2025_even_odd",
        "reason": null
    },
    "id": 1
}
```

Similarly:
- Player on port 8102 receives player_id: "P02"
- Player on port 8103 receives player_id: "P03"
- Player on port 8104 receives player_id: "P04"

The league manager saves contact_endpoint → player_id map and referee_id → contact_endpoint map.

### 8.5 Stage 3: Schedule Creation

After all players and referees registered, the league manager activates create_schedule logic on the players list for Round-Robin.

#### 8.5.1 Schedule for Four Players

**Table 16: Round-Robin Schedule for Four Players**

| Match ID | Player A | Player B |
|----------|----------|----------|
| R1M1 | P01 | P02 |
| R1M2 | P03 | P04 |
| R2M1 | P03 | P01 |
| R2M2 | P04 | P02 |
| R3M1 | P04 | P01 |
| R3M2 | P03 | P02 |

### 8.6 Stage 4: Round Announcement

The league manager sends a ROUND_ANNOUNCEMENT message to all players.

**ROUND_ANNOUNCEMENT - Round Announcement:**
```json
{
    "jsonrpc": "2.0",
    "method": "notify_round",
    "params": {
        "protocol": "league.v2",
        "message_type": "ROUND_ANNOUNCEMENT",
        "sender": "league_manager",
        "timestamp": "2025-01-15T10:10:00Z",
        "conversation_id": "conv-round-1-announce",
        "league_id": "league_2025_even_odd",
        "round_id": 1,
        "matches": [
            {
                "match_id": "R1M1",
                "game_type": "even_odd",
                "player_A_id": "P01",
                "player_B_id": "P02",
                "referee_endpoint": "http://localhost:8001/mcp"
            },
            {
                "match_id": "R1M2",
                "game_type": "even_odd",
                "player_A_id": "P03",
                "player_B_id": "P04",
                "referee_endpoint": "http://localhost:8001/mcp"
            }
        ]
    },
    "id": 10
}
```

From the moment ROUND_ANNOUNCEMENT was sent - the round has logically started. The games themselves start only when the referee invites the participants.

### 8.7 Stage 5: Managing a Single Game

We will describe the R1M1 game flow: Player P01 vs. Player P02, Referee REF01.

#### 8.7.1 Stage 5.1: Game Invitation

The referee transitions the game state to WAITING_FOR_PLAYERS and sends GAME_INVITATION to each player.

**Invitation to P01:**

**GAME_INVITATION to P01 - Game Invitation:**
```json
{
    "jsonrpc": "2.0",
    "method": "handle_game_invitation",
    "params": {
        "protocol": "league.v2",
        "message_type": "GAME_INVITATION",
        "sender": "referee:REF01",
        "timestamp": "2025-01-15T10:15:00Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-ref01-abc123",
        "league_id": "league_2025_even_odd",
        "round_id": 1,
        "match_id": "R1M1",
        "game_type": "even_odd",
        "role_in_match": "PLAYER_A",
        "opponent_id": "P02"
    },
    "id": 1001
}
```

**Invitation to P02:**

**GAME_INVITATION to P02 - Game Invitation:**
```json
{
    "jsonrpc": "2.0",
    "method": "handle_game_invitation",
    "params": {
        "protocol": "league.v2",
        "message_type": "GAME_INVITATION",
        "sender": "referee:REF01",
        "timestamp": "2025-01-15T10:15:00Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-ref01-abc123",
        "league_id": "league_2025_even_odd",
        "round_id": 1,
        "match_id": "R1M1",
        "game_type": "even_odd",
        "role_in_match": "PLAYER_B",
        "opponent_id": "P01"
    },
    "id": 1002
}
```

#### 8.7.2 Stage 5.2: Arrival Confirmations

Each player returns GAME_JOIN_ACK within 5 seconds.

**Confirmation from P01:**

**GAME_JOIN_ACK from P01 - Arrival Confirmation:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "GAME_JOIN_ACK",
        "sender": "player:P01",
        "timestamp": "2025-01-15T10:15:01Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-p01-xyz789",
        "match_id": "R1M1",
        "player_id": "P01",
        "arrival_timestamp": "2025-01-15T10:15:01Z",
        "accept": true
    },
    "id": 1001
}
```

**Confirmation from P02:**

**GAME_JOIN_ACK from P02 - Arrival Confirmation:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "GAME_JOIN_ACK",
        "sender": "player:P02",
        "timestamp": "2025-01-15T10:15:02Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-p02-def456",
        "match_id": "R1M1",
        "player_id": "P02",
        "arrival_timestamp": "2025-01-15T10:15:02Z",
        "accept": true
    },
    "id": 1002
}
```

When the referee received two positive ACKs within the allowed time, it transitions the game state to COLLECTING_CHOICES.

#### 8.7.3 Stage 5.3: Collecting Choices

The referee sends CHOOSE_PARITY_CALL to each player.

**Choice request to P01:**

**CHOOSE_PARITY_CALL to P01 - Choice Request:**
```json
{
    "jsonrpc": "2.0",
    "method": "choose_parity",
    "params": {
        "protocol": "league.v2",
        "message_type": "CHOOSE_PARITY_CALL",
        "sender": "referee:REF01",
        "timestamp": "2025-01-15T10:15:05Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-ref01-abc123",
        "match_id": "R1M1",
        "player_id": "P01",
        "game_type": "even_odd",
        "context": {
            "opponent_id": "P02",
            "round_id": 1,
            "your_standings": {
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
        },
        "deadline": "2025-01-15T10:15:35Z"
    },
    "id": 1101
}
```

**P01's response (chose "even"):**

**CHOOSE_PARITY_RESPONSE from P01 - Choice Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "CHOOSE_PARITY_RESPONSE",
        "sender": "player:P01",
        "timestamp": "2025-01-15T10:15:10Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-p01-xyz789",
        "match_id": "R1M1",
        "player_id": "P01",
        "parity_choice": "even"
    },
    "id": 1101
}
```

**P02's response (chose "odd"):**

**CHOOSE_PARITY_RESPONSE from P02 - Choice Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "CHOOSE_PARITY_RESPONSE",
        "sender": "player:P02",
        "timestamp": "2025-01-15T10:15:12Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-p02-def456",
        "match_id": "R1M1",
        "player_id": "P02",
        "parity_choice": "odd"
    },
    "id": 1102
}
```

When both choices were received correctly and on time, the referee transitions the game state to DRAWING_NUMBER.

#### 8.7.4 Stage 5.4: Number Drawing and Winner Determination

The referee draws a number, for example 8, between 1 and 10. It activates the game rules module:

- drawn_number = 8
- number_parity = "even"
- P01's choice = "even" → correct
- P02's choice = "odd" → wrong
- winner_player_id = "P01"
- status = "WIN"

The game state moves to FINISHED.

#### 8.7.5 Stage 5.5: End Message to Players

The referee sends GAME_OVER to both players:

**GAME_OVER - Game End:**
```json
{
    "jsonrpc": "2.0",
    "method": "notify_match_result",
    "params": {
        "protocol": "league.v2",
        "message_type": "GAME_OVER",
        "sender": "referee:REF01",
        "timestamp": "2025-01-15T10:15:30Z",
        "conversation_id": "conv-r1m1-001",
        "auth_token": "tok-ref01-abc123",
        "match_id": "R1M1",
        "game_type": "even_odd",
        "game_result": {
            "status": "WIN",
            "winner_player_id": "P01",
            "drawn_number": 8,
            "number_parity": "even",
            "choices": {
                "P01": "even",
                "P02": "odd"
            },
            "reason": "P01 chose even, number was 8 (even)"
        }
    },
    "id": 1201
}
```

Each player updates internal state (statistics, history) and returns a general response.

#### 8.7.6 Stage 5.6: Report to League Manager

The referee reports MATCH_RESULT_REPORT to the league:

**MATCH_RESULT_REPORT - Result Report:**
```json
{
    "jsonrpc": "2.0",
    "method": "report_match_result",
    "params": {
        "protocol": "league.v2",
        "message_type": "MATCH_RESULT_REPORT",
        "sender": "referee:REF01",
        "timestamp": "2025-01-15T10:15:35Z",
        "conversation_id": "conv-r1m1-report",
        "auth_token": "tok-ref01-abc123",
        "league_id": "league_2025_even_odd",
        "round_id": 1,
        "match_id": "R1M1",
        "game_type": "even_odd",
        "result": {
            "winner": "P01",
            "score": {
                "P01": 3,
                "P02": 0
            },
            "details": {
                "drawn_number": 8,
                "choices": {
                    "P01": "even",
                    "P02": "odd"
                }
            }
        }
    },
    "id": 1301
}
```

The league manager updates the points table according to the scoring table (win = 3 points).

### 8.8 Stage 6: Round End and Standings Update

Round number 1 ends when MATCH_RESULT_REPORT was received for all round games.

The league manager:

1. Declares the round is closed (can move to round_id=2).
2. Calculates standings table: points, wins, draws, losses, played for each player.
3. Sends LEAGUE_STANDINGS_UPDATE message to all players.

**LEAGUE_STANDINGS_UPDATE - Standings Update:**
```json
{
    "jsonrpc": "2.0",
    "method": "update_standings",
    "params": {
        "protocol": "league.v2",
        "message_type": "LEAGUE_STANDINGS_UPDATE",
        "sender": "league_manager",
        "timestamp": "2025-01-15T10:20:00Z",
        "conversation_id": "conv-round-1-standings",
        "league_id": "league_2025_even_odd",
        "round_id": 1,
        "standings": [
            {
                "rank": 1,
                "player_id": "P01",
                "display_name": "Agent Alpha",
                "played": 1,
                "wins": 1,
                "draws": 0,
                "losses": 0,
                "points": 3
            },
            {
                "rank": 2,
                "player_id": "P03",
                "display_name": "Agent Gamma",
                "played": 1,
                "wins": 0,
                "draws": 1,
                "losses": 0,
                "points": 1
            },
            {
                "rank": 3,
                "player_id": "P04",
                "display_name": "Agent Delta",
                "played": 1,
                "wins": 0,
                "draws": 1,
                "losses": 0,
                "points": 1
            },
            {
                "rank": 4,
                "player_id": "P02",
                "display_name": "Agent Beta",
                "played": 1,
                "wins": 0,
                "draws": 0,
                "losses": 1,
                "points": 0
            }
        ]
    },
    "id": 1401
}
```

After sending the standings update, the league manager sends a ROUND_COMPLETED message to mark the round's end:

**ROUND_COMPLETED - Round End:**
```json
{
    "jsonrpc": "2.0",
    "method": "notify_round_completed",
    "params": {
        "protocol": "league.v2",
        "message_type": "ROUND_COMPLETED",
        "sender": "league_manager",
        "timestamp": "2025-01-15T10:20:05Z",
        "conversation_id": "conv-round-1-complete",
        "league_id": "league_2025_even_odd",
        "round_id": 1,
        "matches_played": 2,
        "next_round_id": 2
    },
    "id": 1402
}
```

### 8.9 Stage 7: League End

After all rounds end, the league manager sends LEAGUE_COMPLETED message:

**LEAGUE_COMPLETED - League End:**
```json
{
    "jsonrpc": "2.0",
    "method": "notify_league_completed",
    "params": {
        "protocol": "league.v2",
        "message_type": "LEAGUE_COMPLETED",
        "sender": "league_manager",
        "timestamp": "2025-01-15T12:00:00Z",
        "conversation_id": "conv-league-complete",
        "league_id": "league_2025_even_odd",
        "total_rounds": 3,
        "total_matches": 6,
        "champion": {
            "player_id": "P01",
            "display_name": "Agent Alpha",
            "points": 7
        },
        "final_standings": [
            {"rank": 1, "player_id": "P01", "points": 7},
            {"rank": 2, "player_id": "P03", "points": 5},
            {"rank": 3, "player_id": "P04", "points": 4},
            {"rank": 4, "player_id": "P02", "points": 2}
        ]
    },
    "id": 2001
}
```

### 8.10 Error Handling

When an error occurs, the league manager or referee sends an appropriate error message.

#### 8.10.1 Authentication Error

**LEAGUE_ERROR - Authentication Error:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocol": "league.v2",
        "message_type": "LEAGUE_ERROR",
        "sender": "league_manager",
        "timestamp": "2025-01-15T10:05:30Z",
        "conversation_id": "conv-error-001",
        "error_code": "E012",
        "error_description": "AUTH_TOKEN_INVALID",
        "context": {
            "provided_token": "tok-invalid-xxx",
            "action": "LEAGUE_QUERY"
        }
    },
    "id": 1502
}
```

#### 8.10.2 Game Error - Response Time

**GAME_ERROR - Game Error:**
```json
{
    "jsonrpc": "2.0",
    "method": "notify_game_error",
    "params": {
        "protocol": "league.v2",
        "message_type": "GAME_ERROR",
        "sender": "referee:REF01",
        "timestamp": "2025-01-15T10:16:00Z",
        "conversation_id": "conv-r1m1-001",
        "match_id": "R1M1",
        "error_code": "E001",
        "error_description": "TIMEOUT_ERROR",
        "affected_player": "P02",
        "action_required": "CHOOSE_PARITY_RESPONSE",
        "retry_count": 0,
        "max_retries": 3,
        "consequence": "Technical loss if no response after retries"
    },
    "id": 1103
}
```

### 8.11 Available Query Tools

The document defines generic MCP tools each agent can expose for debugging and clarification needs.

#### 8.11.1 Standings Query from League Manager

A player who wants to verify their standings calls the league manager:

**LEAGUE_QUERY - Standings Query:**
```json
{
    "jsonrpc": "2.0",
    "method": "league_query",
    "params": {
        "protocol": "league.v2",
        "message_type": "LEAGUE_QUERY",
        "sender": "player:P01",
        "timestamp": "2025-01-15T10:25:00Z",
        "conversation_id": "conv-query-standings-001",
        "auth_token": "tok-p01-xyz789",
        "league_id": "league_2025_even_odd",
        "query_type": "GET_STANDINGS"
    },
    "id": 1501
}
```

The league manager returns result including standings object in identical format to LEAGUE_STANDINGS_UPDATE.

#### 8.11.2 Additional Tools

- **Tool in League Manager:** get_standings - Returns current table status.
- **Tool in Referee:** get_match_state - Returns existing game state (for debugging).
- **Tool in Player:** get_player_state - Returns games history.

### 8.12 Complete Flow Diagram

```
        Start
          │
          ▼
   League Manager Up
          │
          ▼
   Referees Register
          │
          ▼
   Players Register
          │
          ▼
    Create Schedule
          │
          ▼
  Round Announcement
          │
          ▼
    ┌─────────────┐
    │ More        │ Yes
    │ Matches? ───────> Run Match
    └─────┬───────┘        │
          │ No             │
          ▼                │
   Update Standings <──────┘
          │
          ▼
    ┌─────────────┐
    │ More        │ Yes
    │ Rounds? ────────┘
    └─────┬───────┘
          │ No
          ▼
         End
```

### 8.13 Agent Roles Table

**Table 17: Agent Roles in the System**

| Agent | Port | Role in League | Communicates With |
|-------|------|----------------|-------------------|
| LeagueManager | 8000 | League Orchestrator, table, rounds | Referees and players |
| Referee Alpha | 8001 | Games Orchestrator | League manager, players |
| Referee Beta | 8002 | Games Orchestrator | League manager, players |
| P01 PlayerAgent | 8101 | Player, chooses even/odd | Referee, league manager |
| P02 PlayerAgent | 8102 | Player | Referee, league manager |
| P03 PlayerAgent | 8103 | Player | Referee, league manager |
| P04 PlayerAgent | 8104 | Player | Referee, league manager |

### 8.14 Summary

This appendix presented:

- **System Configuration:** Port and terminal allocation for 7 agents.
- **Startup Order:** League manager → Referees → Players.
- **Registration Flow:** REFEREE_REGISTER and LEAGUE_REGISTER with auth_token receipt.
- **Round Management:** ROUND_ANNOUNCEMENT and ROUND_COMPLETED.
- **Game Management:** From GAME_INVITATION to GAME_OVER.
- **Standings Update:** MATCH_RESULT_REPORT and LEAGUE_STANDINGS_UPDATE.
- **League End:** LEAGUE_COMPLETED with champion announcement.
- **Error Handling:** LEAGUE_ERROR and GAME_ERROR.
- **Queries:** LEAGUE_QUERY for receiving updated information.

All communication is done via JSON-RPC 2.0 over HTTP. All messages include a uniform Envelope with required fields: protocol, message_type, sender, timestamp (in UTC timezone), and conversation_id. The orchestrators (league manager and referees) manage the message flow at any moment.

---

## 9. League Data Protocol

### 9.1 Introduction: The Genetic Code of the Agent Society

When we build a society of autonomous agents - players, referees, and league managers - we are essentially creating a new digital culture. Just like any human society, here too three critical foundations are required:

1. **Shared Rules** - The protocol we defined in previous chapters.
2. **Collective Memory** - The ability to store and retrieve historical information.
3. **Genetic Code** - The configuration that defines the DNA of each agent.

This appendix describes "The Database on JSON Files" - a three-layer architecture that allows the system to grow to a scale of thousands of agents and leagues.

### 9.2 Three-Layer Architecture

```
┌────────────────────────────────────┐
│ config/    Configuration Layer     │ ← Static definitions
├────────────────────────────────────┤
│ data/      Runtime Data Layer      │ ← Dynamic state and history
├────────────────────────────────────┤
│ logs/      Logs Layer              │ ← Tracking and debugging
└────────────────────────────────────┘
```

#### 9.2.1 Guiding Principles

Every file in the system meets the following principles:

- **Unique Identifier (id):** Every main object receives a unique identifier.
- **Schema Version (schema_version):** Enables future migrations.
- **Timestamp (last_updated):** In UTC/ISO-8601 format.
- **Protocol Compatibility:** All fields match league.v2.

### 9.3 config/ - Configuration Layer

This layer contains the "genetic code" of the system - static definitions read at agent startup.

#### 9.3.1 config/system.json - Global System File

- **Purpose:** Global parameters for the entire system.
- **Users:** All agents, supreme Orchestrator.
- **Location:** SHARED/config/system.json

This file defines default values for:

- **Network (network):** Ports and addresses.
- **Security (security):** Tokens and TTL.
- **Timeouts:** Match protocol settings in Chapter 2.
- **Retry Policy (retry_policy):** Matches protocol settings.

**Example: system.json structure (excerpt):**
```json
{
    "schema_version": "1.0.0",
    "system_id": "league_system_prod",
    "protocol_version": "league.v2",
    "timeouts": {
        "move_timeout_sec": 30,
        "generic_response_timeout_sec": 10
    },
    "retry_policy": {
        "max_retries": 3,
        "backoff_strategy": "exponential"
    }
}
```

#### 9.3.2 config/agents/agents_config.json - Agent Registration

- **Purpose:** Central management of thousands of agents.
- **Users:** League manager, Deployment tools.
- **Location:** SHARED/config/agents/agents_config.json

This file contains the "citizens register" of the agent society:

- **league_manager** - League manager details.
- **referees[]** - List of all registered referees.
- **players[]** - List of all registered players.

#### 9.3.3 config/leagues/<league_id>.json - League Configuration

- **Purpose:** League-specific settings.
- **Users:** League manager, referees.
- **Location:** SHARED/config/leagues/league_2025_even_odd.json

Each league is an independent "state" with its own rules:

**Example: League configuration (excerpt):**
```json
{
    "league_id": "league_2025_even_odd",
    "game_type": "even_odd",
    "status": "ACTIVE",
    "scoring": {
        "win_points": 3,
        "draw_points": 1,
        "loss_points": 0
    },
    "participants": {
        "min_players": 2,
        "max_players": 10000
    }
}
```

#### 9.3.4 config/games/games_registry.json - Game Types Registration

- **Purpose:** Registration of all supported game types.
- **Users:** Referees (for rules module loading), league manager.
- **Location:** SHARED/config/games/games_registry.json

The system supports multiple game types. Each game defines:

- **game_type** - Unique identifier.
- **rules_module** - Rules module for loading.
- **max_round_time_sec** - Maximum time per round.

#### 9.3.5 config/defaults/ - Agent Defaults

- **Purpose:** Default values by agent type.
- **Files:** referee.json, player.json
- **Location:** SHARED/config/defaults/

These files allow a new agent to start operating with reasonable settings without defining every parameter separately.

### 9.4 data/ - Runtime Data Layer

If the configuration layer is the "genetic code", the runtime data layer is the "historical memory" of the society. Here all events that occur in the system are preserved.

#### 9.4.1 data/leagues/<league_id>/standings.json - Standings Table

- **Purpose:** Current standings status of the league.
- **Updater:** League manager (after MATCH_RESULT_REPORT).
- **Location:** SHARED/data/leagues/league_2025_even_odd/standings.json

**Example: Standings table structure:**
```json
{
    "schema_version": "1.0.0",
    "league_id": "league_2025_even_odd",
    "version": 12,
    "rounds_completed": 3,
    "standings": [
        {
            "rank": 1,
            "player_id": "P01",
            "display_name": "Agent Alpha",
            "wins": 4, "draws": 1, "losses": 1,
            "points": 13
        }
    ]
}
```

#### 9.4.2 data/leagues/<league_id>/rounds.json - Rounds History

- **Purpose:** Documentation of all rounds that occurred.
- **Updater:** League manager (after ROUND_COMPLETED).
- **Location:** SHARED/data/leagues/league_2025_even_odd/rounds.json

#### 9.4.3 data/matches/<league_id>/<match_id>.json - Single Game Data

- **Purpose:** Full documentation of a single game.
- **Updater:** The referee who managed the game.
- **Location:** SHARED/data/matches/league_2025_even_odd/R1M1.json

This file is the "identity card" of the game and contains:

- **lifecycle** - Game state and times.
- **transcript[]** - All messages exchanged (move history).
- **result** - Final result (matches GAME_OVER).

#### 9.4.4 data/players/<player_id>/history.json - Player History

- **Purpose:** Player's "personal memory".
- **User:** The player themselves (for strategy building).
- **Location:** SHARED/data/players/P01/history.json

A smart player can use this file as "memory" for improving their strategy:

**Example: Player history:**
```json
{
    "player_id": "P01",
    "stats": {
        "total_matches": 20,
        "wins": 12, "losses": 5, "draws": 3
    },
    "matches": [
        {
            "match_id": "R1M1",
            "opponent_id": "P02",
            "result": "WIN",
            "my_choice": "even",
            "opponent_choice": "odd"
        }
    ]
}
```

### 9.5 logs/ - Logs Layer

This layer is the "nervous system" of the society - it allows us to see what is really happening in the distributed system.

#### 9.5.1 logs/league/<league_id>/league.log.jsonl - Central League Log

- **Format:** JSONLines (each line is a separate JSON object).
- **Users:** DevOps, technical support.
- **Location:** SHARED/logs/league/league_2025_even_odd/league.log.jsonl

**Example: League log entry:**
```json
{
    "timestamp": "2025-01-15T10:15:00Z",
    "component": "league_manager",
    "event_type": "ROUND_ANNOUNCEMENT_SENT",
    "level": "INFO",
    "details": {"round_id": 1, "matches_count": 2}
}
```

#### 9.5.2 logs/agents/<agent_id>.log.jsonl - Agent Log

- **Purpose:** Per-agent tracking for debugging.
- **Users:** Agent developers.
- **Location:** SHARED/logs/agents/P01.log.jsonl

Each agent documents messages it sends and receives, which enables End-to-End Trace of any interaction in the system.

### 9.6 Files Summary Table

**Table 18: Configuration and Data Files Summary**

| Layer | Path | Purpose | User |
|-------|------|---------|------|
| config | config/system.json | Global parameters | All agents |
| config | config/agents/ | Agent registration | League manager |
| config | config/leagues/ | League settings | League manager |
| config | config/games/ | Games registration | Referees |
| config | config/defaults/ | Defaults | Agents |
| runtime | data/.../standings.json | Standings table | Everyone |
| runtime | data/.../rounds.json | Rounds history | League manager |
| runtime | data/matches/ | Game details | Analytics |
| runtime | data/players/ | Personal history | Player |
| logs | logs/league/ | Central log | DevOps |
| logs | logs/agents/ | Agent log | Developers |

### 9.7 Using Shared Files

All example files described in this appendix are available in the shared directory:

```
L07/SHARED/
```

Students are invited to use these files as a basis for their agent implementations. The files include:

- Complete examples for each file type.
- Data matching league.v2 protocol.
- Recommended directory structure for the project.

### 9.8 Summary

The three-layer architecture we presented - configuration, runtime data, and logs - provides the infrastructure required for building an agent system at scale of thousands.

Just like in a human society:

- Configuration is the "constitution" - the fundamental rules everyone knows.
- Runtime data is the "historical archive" - the collective memory.
- Logs are the "journalism" - documentation of what's happening in real time.

This structure prepares the system for growth of thousands of agents and leagues, while maintaining order, consistency, and tracking capability.

---

## 10. Python Toolkit

### 10.1 Introduction: From Configuration to Code

In the previous appendix, we presented the JSON file-based data architecture - three layers of configuration, runtime data, and logs. But how does an individual agent actually access this data?

This appendix presents league_sdk - a Python library that bridges between the JSON files and the objects the agents use. The library implements two main design patterns:

1. **Dataclasses** - Typed models that reflect the JSON structure.
2. **Repository Pattern** - An abstraction layer for data access.

### 10.2 Library Structure

```
league_sdk/
├── __init__.py           # Package entry point
├── config_models.py      # Data classes
├── config_loader.py      # Configuration loading
├── repositories.py       # Runtime data management
└── logger.py             # Log recording
```

### 10.3 config_models.py - Typed Models

#### 10.3.1 Approach: Dataclasses

Python 3.7+ provides the @dataclass decorator that enables defining data classes concisely. Each field in JSON becomes a field in a class with a defined type:

**Example: Dataclass definition:**
```python
from dataclasses import dataclass
from typing import List

@dataclass
class NetworkConfig:
    base_host: str
    default_league_manager_port: int
    default_referee_port_range: List[int]
    default_player_port_range: List[int]
```

#### 10.3.2 System Configuration Models

The file defines all models matching config/system.json:

**Global configuration models:**
```python
@dataclass
class SecurityConfig:
    enable_auth_tokens: bool
    token_length: int
    token_ttl_hours: int

@dataclass
class TimeoutsConfig:
    register_referee_timeout_sec: int
    register_player_timeout_sec: int
    game_join_ack_timeout_sec: int
    move_timeout_sec: int
    generic_response_timeout_sec: int

@dataclass
class SystemConfig:
    schema_version: str
    system_id: str
    protocol_version: str
    default_league_id: str
    network: NetworkConfig
    security: SecurityConfig
    timeouts: TimeoutsConfig
    # ...additional fields
```

#### 10.3.3 Agent Models

Each agent type receives its own configuration class:

**Agent configuration models:**
```python
@dataclass
class RefereeConfig:
    referee_id: str
    display_name: str
    endpoint: str
    version: str
    game_types: List[str]
    max_concurrent_matches: int
    active: bool = True

@dataclass
class PlayerConfig:
    player_id: str
    display_name: str
    version: str
    preferred_leagues: List[str]
    game_types: List[str]
    default_endpoint: str
    active: bool = True
```

#### 10.3.4 League Models

League-specific settings include scheduling, scoring, and participants:

**League configuration models:**
```python
@dataclass
class ScoringConfig:
    win_points: int
    draw_points: int
    loss_points: int
    technical_loss_points: int
    tiebreakers: List[str]

@dataclass
class LeagueConfig:
    schema_version: str
    league_id: str
    display_name: str
    game_type: str
    status: str
    scoring: ScoringConfig
    # ...additional fields
```

### 10.4 ConfigLoader - Configuration Loader

#### 10.4.1 The Principle: Lazy Loading with Cache

The ConfigLoader class implements the Lazy Loading pattern - configuration files are loaded only when needed and cached for repeated access:

**ConfigLoader structure:**
```python
class ConfigLoader:
    def __init__(self, root: Path = CONFIG_ROOT):
        self.root = root
        self._system = None      # lazy cache
        self._agents = None      # lazy cache
        self._leagues = {}       # league_id -> LeagueConfig
    
    def load_system(self) -> SystemConfig:
        """Load global system configuration."""
        if self._system:
            return self._system
        
        path = self.root / "system.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self._system = SystemConfig(...)
        return self._system
```

#### 10.4.2 Loading Methods

ConfigLoader provides a uniform interface for loading all configuration types:

**Table 19: ConfigLoader Loading Methods**

| Method | Returns | Description |
|--------|---------|-------------|
| load_system() | SystemConfig | Global configuration |
| load_agents() | AgentsConfig | List of all agents |
| load_league(id) | LeagueConfig | Specific league configuration |
| load_games_registry() | GamesRegistry | Game types registration |

#### 10.4.3 Helper Methods

In addition to direct loading, the class provides convenience methods for searching:

**Helper methods:**
```python
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
```

### 10.5 Repositories - Data Repositories

#### 10.5.1 Repository Pattern

While ConfigLoader handles static configuration, the repositories layer handles dynamic data. Each repository is responsible for reading, updating, and saving a specific data type.

#### 10.5.2 StandingsRepository - Standings Table Repository

**Standings table repository:**
```python
class StandingsRepository:
    def __init__(self, league_id: str, data_root: Path = DATA_ROOT):
        self.league_id = league_id
        self.path = data_root / "leagues" / league_id / "standings.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict:
        """Load standings from JSON file."""
        if not self.path.exists():
            return {"schema_version": "1.0.0", "standings": []}
        return json.loads(self.path.read_text(encoding="utf-8"))
    
    def save(self, standings: Dict) -> None:
        """Save standings to JSON file."""
        standings["last_updated"] = datetime.utcnow().isoformat() + "Z"
        self.path.write_text(json.dumps(standings, indent=2))
    
    def update_player(self, player_id: str, result: str, points: int):
        """Update a player's standings after a match."""
        standings = self.load()
        # ... update logic
        self.save(standings)
```

#### 10.5.3 Additional Repositories

The library includes additional repositories for runtime data management:

**Table 20: Available Data Repositories**

| Repository | File | Role |
|------------|------|------|
| StandingsRepository | standings.json | League standings table |
| RoundsRepository | rounds.json | Rounds history |
| MatchRepository | <match_id>.json | Single game data |
| PlayerHistoryRepository | history.json | Player history |

### 10.6 JsonLogger - Log Recording

#### 10.6.1 JSONLines Format

The library uses JSONL (JSON Lines) format - each line in the log file is an independent JSON object. This format enables:

- Adding new records efficiently (append-only).
- Reading and analysis with standard tools.
- Streaming logs in real time.

#### 10.6.2 Logger Class

**JsonLogger class:**
```python
class JsonLogger:
    def __init__(self, component: str, league_id: str | None = None):
        self.component = component
        
        # Determine log directory
        if league_id:
            subdir = LOG_ROOT / "league" / league_id
        else:
            subdir = LOG_ROOT / "system"
        
        subdir.mkdir(parents=True, exist_ok=True)
        self.log_file = subdir / f"{component}.log.jsonl"
    
    def log(self, event_type: str, level: str = "INFO", **details):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "component": self.component,
            "event_type": event_type,
            "level": level,
            **details,
        }
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

#### 10.6.3 Convenience Methods

The logger provides methods for different log levels and common events:

**Logger convenience methods:**
```python
def debug(self, event_type: str, **details):
    self.log(event_type, level="DEBUG", **details)

def info(self, event_type: str, **details):
    self.log(event_type, level="INFO", **details)

def warning(self, event_type: str, **details):
    self.log(event_type, level="WARNING", **details)

def error(self, event_type: str, **details):
    self.log(event_type, level="ERROR", **details)

def log_message_sent(self, message_type: str, recipient: str, **details):
    self.debug("MESSAGE_SENT", message_type=message_type,
               recipient=recipient, **details)
```

### 10.7 Usage in Agents

#### 10.7.1 Example: League Manager

**Using ConfigLoader in League Manager:**
```python
from league_sdk import ConfigLoader, JsonLogger

class LeagueManager:
    def __init__(self, league_id: str):
        loader = ConfigLoader()
        self.system_cfg = loader.load_system()
        self.agents_cfg = loader.load_agents()
        self.league_cfg = loader.load_league(league_id)
        self.logger = JsonLogger("league_manager", league_id)
        
        # Build lookup maps
        self.referees_by_id = {
            r.referee_id: r.endpoint
            for r in self.agents_cfg.referees if r.active
        }
    
    def get_timeout_for_move(self) -> int:
        return self.system_cfg.timeouts.move_timeout_sec
```

#### 10.7.2 Example: Referee Agent

**Using ConfigLoader in Referee:**
```python
from league_sdk import ConfigLoader, JsonLogger

class RefereeAgent:
    def __init__(self, referee_id: str, league_id: str):
        loader = ConfigLoader()
        self.system_cfg = loader.load_system()
        self.league_cfg = loader.load_league(league_id)
        self.self_cfg = loader.get_referee_by_id(referee_id)
        self.logger = JsonLogger(f"referee:{referee_id}", league_id)
    
    def register_to_league(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "register_referee",
            "params": {
                "protocol": self.system_cfg.protocol_version,
                "message_type": "REFEREE_REGISTER_REQUEST",
                "referee_meta": {
                    "display_name": self.self_cfg.display_name,
                    "version": self.self_cfg.version,
                    "game_types": self.self_cfg.game_types,
                }
            }
        }
        # ... send request
```

#### 10.7.3 Example: Error Logging

**TIMEOUT error logging:**
```python
logger = JsonLogger("referee:REF01", "league_2025_even_odd")

logger.error(
    "GAME_ERROR",
    match_id="R1M1",
    error_code="TIMEOUT_MOVE",
    player_id="P02",
    timeout_sec=30,
)

# Output to logs/league/league_2025_even_odd/referee_REF01.log.jsonl:
# {"timestamp":"2025-01-15T10:15:00Z","component":"referee:REF01",
#  "event_type":"GAME_ERROR","level":"ERROR","match_id":"R1M1",...}
```

### 10.8 Summary

The league_sdk library provides a clean abstraction layer between JSON files and agent code:

- **config_models.py** - Defines safe types for every data structure.
- **config_loader.py** - Provides convenient access to configuration with cache.
- **repositories.py** - Manages runtime data in Repository pattern.
- **logger.py** - Enables structured log recording in JSONL format.

Using this library ensures:

1. **Consistency** - All agents use the same models and data.
2. **Maintainability** - Changes in data structure are concentrated in one place.
3. **Type Safety** - Errors are caught at code writing time.
4. **Debugging Capability** - Structured logs enable easy tracking of issues.

The library is available in the directory:
```
L07/SHARED/league_sdk/
```

---

## 11. Project Structure

### 11.1 Introduction: The Road Map

After we've learned the protocol, JSON messages, data architecture, and Python library - it's time to see the complete picture. This appendix presents the recommended file and directory structure for the league project, so that every student can start working with an organized and ready foundation.

### 11.2 Main Directory Tree

```
L07/
├── SHARED/          # Shared resources
├── agents/          # Agent code
└── doc/             # Documentation
```

**Table 21: Project Base Directories**

| Directory | Description |
|-----------|-------------|
| SHARED/ | Shared resources - configuration, data, logs, and SDK library |
| agents/ | Agent code - each agent in a separate directory |
| doc/ | Project documentation - documents and specifications |

### 11.3 SHARED/ - Shared Resources Directory

This directory contains all resources shared by all agents in the system.

```
SHARED/
├── config/                          # Configuration layer
│   ├── system.json                  # Global system settings
│   ├── agents/
│   │   └── agents_config.json       # All agents registry
│   ├── leagues/
│   │   └── league_2025_even_odd.json
│   ├── games/
│   │   └── games_registry.json      # Supported game types
│   └── defaults/
│       ├── referee.json             # Default referee settings
│       └── player.json              # Default player settings
│
├── data/                            # Runtime data layer
│   ├── leagues/
│   │   └── league_2025_even_odd/
│   │       ├── standings.json       # Current standings
│   │       └── rounds.json          # Round history
│   ├── matches/
│   │   └── league_2025_even_odd/
│   │       ├── R1M1.json            # Match R1M1 data
│   │       └── R1M2.json            # Match R1M2 data
│   └── players/
│       ├── P01/
│       │   └── history.json         # P01 match history
│       └── P02/
│           └── history.json         # P02 match history
│
├── logs/                            # Logging layer
│   ├── league/
│   │   └── league_2025_even_odd/
│   │       └── league.log.jsonl
│   ├── agents/
│   │   ├── REF01.log.jsonl
│   │   ├── P01.log.jsonl
│   │   └── P02.log.jsonl
│   └── system/
│       └── orchestrator.log.jsonl
│
└── league_sdk/                      # Python SDK
    ├── __init__.py
    ├── config_models.py             # Dataclass definitions
    ├── config_loader.py             # ConfigLoader class
    ├── repositories.py              # Data repositories
    └── logger.py                    # JsonLogger class
```

### 11.4 agents/ - Agents Directory

Each agent lives in a separate directory with a uniform structure:

```
agents/
├── league_manager/
│   ├── main.py              # Entry point
│   ├── handlers.py          # Message handlers
│   ├── scheduler.py         # Round scheduling
│   └── requirements.txt
│
├── referee_REF01/
│   ├── main.py              # Entry point
│   ├── game_logic.py        # Even/Odd rules
│   ├── handlers.py          # Message handlers
│   └── requirements.txt
│
├── player_P01/
│   ├── main.py              # Entry point
│   ├── strategy.py          # Playing strategy
│   ├── handlers.py          # Message handlers
│   └── requirements.txt
│
└── player_P02/
    ├── main.py
    ├── strategy.py
    ├── handlers.py
    └── requirements.txt
```

#### 11.4.1 Typical Agent Structure

**Table 22: Typical Agent Files**

| File | Role |
|------|------|
| main.py | Entry point - server initialization and configuration loading |
| handlers.py | Handling incoming messages by type |
| strategy.py | (For players) Decision-making logic |
| game_logic.py | (For referees) Game rules |
| requirements.txt | Python dependencies |

### 11.5 doc/ - Documentation Directory

```
doc/
├── protocol-spec.md                 # Protocol specification
├── message-examples/                # JSON message examples
│   ├── registration/
│   │   ├── referee_register_request.json
│   │   └── player_register_request.json
│   ├── game-flow/
│   │   ├── game_start.json
│   │   ├── move_request.json
│   │   └── game_over.json
│   └── errors/
│       ├── timeout_error.json
│       └── invalid_move.json
└── diagrams/
    ├── architecture.png
    └── message-flow.png
```

### 11.6 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     League Manager                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Referee  │    │ Player   │    │ Player   │  ← JSON-RPC Communication
    │  REF01   │    │   P01    │    │   P02    │
    └──────────┘    └──────────┘    └──────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │                   SHARED Resources                       │
    ├──────────────────┬──────────────────┬───────────────────┤
    │ config/          │ data/            │ logs/             │
    │ - Configuration  │ - Runtime data   │ - Logs            │
    │                  │                  │                   │
    │ league_sdk/      │                  │                   │
    │ - Python library │                  │                   │
    └──────────────────┴──────────────────┴───────────────────┘
```

### 11.7 Data Flow

#### 11.7.1 Reading and Writing

**Table 23: File Access Permissions**

| File/Directory | Reads | Writes | Notes |
|----------------|-------|--------|-------|
| config/* | Everyone | System admin | Read-only for agents |
| standings.json | Everyone | League manager | Update after game |
| rounds.json | Everyone | League manager | Rounds history |
| matches/*.json | Everyone | Referee | File per game |
| history.json | The player | The player | Personal history |
| logs/* | DevOps | Each agent | Only their own log |

### 11.8 Installation and Running

#### 11.8.1 Prerequisites

- Python 3.10+
- pip or poetry for package management
- Access to SHARED/ directory

#### 11.8.2 Installing Dependencies

```bash
# Install league_sdk
cd SHARED
pip install -e league_sdk/

# Install agent dependencies
cd ../agents/player_P01
pip install -r requirements.txt
```

#### 11.8.3 Running an Agent

```bash
# Start League Manager
cd agents/league_manager
python main.py --league-id league_2025_even_odd

# Start Referee
cd agents/referee_REF01
python main.py --referee-id REF01 \
    --league-id league_2025_even_odd

# Start Player
cd agents/player_P01
python main.py --player-id P01 \
    --league-id league_2025_even_odd
```

### 11.9 Complete File List

Below is the complete list of all files in the project:

```
L07/
├── SHARED/
│   ├── config/
│   │   ├── system.json
│   │   ├── agents/agents_config.json
│   │   ├── leagues/league_2025_even_odd.json
│   │   ├── games/games_registry.json
│   │   └── defaults/{referee,player}.json
│   ├── data/
│   │   ├── leagues/<league_id>/{standings,rounds}.json
│   │   ├── matches/<league_id>/<match_id>.json
│   │   └── players/<player_id>/history.json
│   ├── logs/
│   │   ├── league/<league_id>/*.log.jsonl
│   │   ├── agents/*.log.jsonl
│   │   └── system/*.log.jsonl
│   └── league_sdk/
│       ├── __init__.py
│       ├── config_models.py
│       ├── config_loader.py
│       ├── repositories.py
│       └── logger.py
├── agents/
│   ├── league_manager/{main,handlers,scheduler}.py
│   ├── referee_REF01/{main,handlers,game_logic}.py
│   └── player_*/{main,handlers,strategy}.py
└── doc/
    ├── protocol-spec.md
    └── message-examples/**/*.json
```

### 11.10 Summary

The project structure presented in this appendix provides:

1. **Clear Separation** - Each component in its own directory.
2. **Shared Resources** - SHARED/ centralizes all data.
3. **Agent Independence** - Each agent can operate independently.
4. **Structured Documentation** - Examples and specifications in doc/.
5. **Extensibility** - Easy to add new leagues and agents.

The complete files are available in the directory:
```
L07/SHARED/
```

It is recommended to clone the structure and start building your agents!

---

## 12. References

1. Y. Segal, *AI Agents with MCP*. Dr. Yoram Segal, 2025, Hebrew edition.

2. Anthropic, *Model context protocol specification*, 2024. [Online]. Available: https://modelcontextprotocol.io/

3. JSON-RPC Working Group, *Json-rpc 2.0 specification*, 2010. [Online]. Available: https://www.jsonrpc.org/specification

4. K. Stratis, *AI Agents with MCP*. O'Reilly Media, 2025, Early Release.
