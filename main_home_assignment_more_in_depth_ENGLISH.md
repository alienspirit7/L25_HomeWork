# Homework Exercise: Even/Odd League

**Dr. Yoram Segal**

© Dr. Yoram Segal 2025 - All Rights Reserved

Version 1.0

---

## Table of Contents

1. [Introduction: AI Agents and MCP Protocol](#1-introduction-ai-agents-and-mcp-protocol)
2. [General League Protocol](#2-general-league-protocol)
3. [Even/Odd Game](#3-evenodd-game)
4. [JSON Message Structures](#4-json-message-structures)
5. [Implementation Guide](#5-implementation-guide)
6. [Homework Requirements](#6-homework-requirements)
7. [Learning MCP Through the League Exercise](#7-learning-mcp-through-the-league-exercise)
8. [References](#8-references)

---

## 1. Introduction: AI Agents and MCP Protocol

### 1.1 What is an AI Agent?

An AI Agent is autonomous software. The agent receives information from the environment. It processes the information. Then it performs actions.

An AI Agent is different from a regular program. A regular program executes predetermined instructions. An AI Agent decides on its own what to do. The decision is based on the current state.

#### 1.1.1 Characteristics of an AI Agent

Every AI Agent has several characteristics:

- **Autonomy** – The agent operates independently.
- **Perception** – The agent absorbs information from the environment.
- **Action** – The agent affects the environment.
- **Goal-orientation** – The agent has a defined goal.

In Dr. Yoram Segal's book "AI Agents with MCP" [1], it is explained how agents communicate. The book presents the MCP protocol in detail. We will use these principles in the exercise.

### 1.2 MCP Protocol – Model Context Protocol

MCP is a communication protocol. The protocol was developed by Anthropic. It enables AI agents to communicate with each other.

#### 1.2.1 Protocol Principles

The protocol is based on several principles:

1. **Structured messages** – Every message is a JSON object.
2. **JSON-RPC 2.0 standard** – The protocol uses this standard.
3. **Tools** – Agents expose functions as "tools".
4. **Flexible transport** – Can use HTTP or stdio.

#### 1.2.2 Host/Server Architecture

In an MCP system, there are two types of components:

- **MCP Server** – A component that provides services. The server exposes "tools" that can be called. Each tool is a function with defined parameters.

- **Host** – A component that coordinates between servers. The host sends requests to servers. It receives responses and processes them.

```
┌─────────────────────────────────────────────────────────────┐
│                          Host                               │
│                     (Orchestrator)                          │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ JSON-RPC           │ JSON-RPC           │ JSON-RPC
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  MCP Server 1   │  │  MCP Server 2   │  │  MCP Server 3   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 1.3 HTTP Transport on localhost

In this exercise, we will use HTTP transport. Each agent will operate on a different port on localhost.

#### 1.3.1 Port Definitions

We define fixed ports for each agent:

| Agent | Port |
|-------|------|
| League Manager | 8000 |
| Referee | 8001 |
| Players | 8101-8104 |

Each agent implements a simple HTTP server. The server receives POST requests at the `/mcp` path. The request content is JSON-RPC 2.0.

#### 1.3.2 Example Agent Address

**League Manager server address:**
```
http://localhost:8000/mcp
```

**First player server address:**
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

**Message fields:**

- **jsonrpc** – Protocol version, always "2.0".
- **method** – Name of the tool to invoke.
- **params** – Parameters for the tool.
- **id** – Unique identifier for the request.

### 1.5 Exercise Goal

In this exercise, we will build a league system for AI agents. The system will include three types of agents:

1. **League Manager** – Manages the league.
2. **Referee** – Manager for a single game.
3. **Player Agents** – Participate in games.

The specific game in this exercise is "Even/Odd". The general protocol allows replacing the game in the future. It will be possible to use Tic-Tac-Toe, 21 Questions, or other games.

#### 1.5.1 Learning Objective

At the end of the exercise, you will be able to:

- Understand the MCP protocol.
- Build a simple MCP server.
- Communicate between different agents.
- Participate in a league against other students.

**Important:** All students will use the same protocol. This will allow your agents to play against each other.

---

## 2. General League Protocol

### 2.1 Protocol Principles

The protocol defines uniform rules. The rules enable different agents to communicate. Each student can implement an agent in any language they want – as long as the agent respects the protocol, they will participate in the league.

#### 2.1.1 Separation into Three Layers

The system is composed of three layers:

1. **League Layer** – Tournament management, player registration, standings table.
2. **Refereeing Layer** – Single game management, move validation, winner announcement.
3. **Game Rules Layer** – Specific game logic (Even/Odd, Tic-Tac-Toe, etc.).

This separation is important. It allows replacing the game layer. The general protocol will remain unchanged.

### 2.2 Agent Types

#### 2.2.1 League Manager

The League Manager is a single agent. It is responsible for:

- Registering players to the league.
- Creating the game schedule (Round-Robin).
- Receiving results from referees.
- Calculating and publishing the standings table.

The League Manager operates as an MCP server on port 8000.

#### 2.2.2 Referee

The Referee is the manager for a single game. It is responsible for:

- Inviting two players to a game.
- Managing game turns.
- Validating move legality.
- Announcing the result and reporting to the league.

The Referee operates as an MCP server on port 8001.

#### 2.2.3 Player Agent

The Player Agent represents a player in the league. It is responsible for:

- Registering to the league.
- Receiving invitations to games.
- Choosing moves in the game.
- Updating internal state based on results.

Each player operates on a separate port (8101-8104).

### 2.3 Identifiers in the Protocol

Each component in the system is uniquely identified.

**Table 1: Identifiers in the League Protocol**

| Identifier Name | Type | Description |
|-----------------|------|-------------|
| league_id | String | Unique league identifier |
| round_id | Integer | Round number in the league |
| match_id | String | Single match identifier |
| game_type | String | Game type |
| player_id | String | Player identifier |
| conversation_id | String | Conversation identifier |

#### 2.3.1 Identifier Examples

- **league_id:** "league_2025_even_odd"
- **round_id:** 1, 2, 3, ...
- **match_id:** "R1M1" (Round 1, Match 1)
- **game_type:** "even_odd" or "tic_tac_toe"
- **player_id:** "P01", "P02", ..., "P20"

### 2.4 General Message Structure

Every message in the protocol contains fixed fields.

**Message Structure in the League Protocol:**
```json
{
    "protocol": "league.v1",
    "message_type": "...",
    "league_id": "...",
    "round_id": 1,
    "match_id": "R1M3",
    "conversation_id": "uuid-or-similar",
    "sender": "league_manager | referee | player:P01",
    "timestamp": "ISO-8601"
}
```

#### 2.4.1 Field Descriptions

- **protocol** – Fixed, protocol version "league.v1".
- **message_type** – Message type (registration, invitation, move, etc.).
- **league_id** – Current league identifier.
- **round_id** – Round number.
- **match_id** – Match identifier.
- **conversation_id** – Conversation identifier.
- **sender** – Who sent the message.
- **timestamp** – Timestamp in ISO-8601 format.

### 2.5 General League Flow

#### 2.5.1 Stage 1: Player Registration

Initially, each player registers to the league. The player sends a registration request to the League Manager. The League Manager assigns a player_id and confirms.

```
┌─────────────────┐                    ┌─────────────────┐
│  Player Agent   │                    │ League Manager  │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │       REGISTER_REQUEST               │
         │─────────────────────────────────────>│
         │                                      │
         │       REGISTER_RESPONSE              │
         │<─────────────────────────────────────│
         │                                      │
```

#### 2.5.2 Stage 2: Game Schedule Creation

After all players have registered, the League Manager creates a game schedule. The schedule is based on the Round-Robin method. Each player plays against every other player.

#### 2.5.3 Stage 3: Round Announcement

Before each round, the League Manager publishes a ROUND_ANNOUNCEMENT message. The message details all games in the round.

#### 2.5.4 Stage 4: Game Management

The Referee invites players to a game. It manages the game according to the game rules. At the end, it reports the result to the League Manager.

#### 2.5.5 Stage 5: Standings Update

After each round, the League Manager updates the standings table. It publishes the table to all players.

### 2.6 General Flow Diagram

```
        ┌───────────────────┐
        │       Start       │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Register Players  │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Create Schedule   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   More Matches?   │◄──────────────┐
        └─────────┬─────────┘               │
                  │                         │
            Yes   │   No                    │
         ┌────────┴────────┐                │
         │                 │                │
         ▼                 ▼                │
┌─────────────────┐  ┌───────────┐          │
│   Run Match     │  │    End    │          │
└────────┬────────┘  └───────────┘          │
         │                                  │
         ▼                                  │
┌───────────────────┐                       │
│ Update Standings  │───────────────────────┘
└───────────────────┘
```

### 2.7 Important Principles

#### 2.7.1 Single Source of Truth

The Referee is the source of truth for game state. Players do not save their own state. They rely on information the Referee sends.

#### 2.7.2 Communication Through Orchestrator

Players do not communicate directly with each other. All communication goes through the Referee or League Manager. This ensures the protocol is maintained.

#### 2.7.3 Response Times

Each request has a maximum response time. If a player does not respond in time – they lose technically. The default is 30 seconds.

#### 2.7.4 Error Handling

If a player sends an illegal move:

1. The Referee sends a MOVE_REJECTED message.
2. The player gets another chance.
3. After 3 failed attempts – technical loss.

---

## 3. Even/Odd Game

### 3.1 Game Description

The Even/Odd game is a simple game. It is suitable for demonstrating the league protocol.

#### 3.1.1 Game Rules

1. Two players participate in the game.
2. Each player chooses "even" or "odd".
3. Choices are made simultaneously, without knowing the opponent's choice.
4. The Referee draws a number between 1 and 10.
5. If the number is even – whoever chose "even" wins.
6. If the number is odd – whoever chose "odd" wins.
7. If both chose the same thing and both guessed correctly/incorrectly – draw.

#### 3.1.2 Game Example

Suppose a game between Player A and Player B:

**Table 2: Example of Even/Odd Game**

| Player A Choice | Player B Choice | Number | Result |
|-----------------|-----------------|--------|--------|
| even | odd | 8 (even) | Player A wins |
| even | odd | 7 (odd) | Player B wins |
| odd | odd | 4 (even) | Draw |

### 3.2 Single Game Flow

#### 3.2.1 Stage 1: Game Invitation

The Referee sends an invitation to both players. The invitation includes:

- Match identifier (match_id).
- Round identifier (round_id).
- Game type (game_type).

#### 3.2.2 Stage 2: Arrival Confirmation

Each player confirms receipt of the invitation. The confirmation includes a timestamp.

#### 3.2.3 Stage 3: Choice Collection

The Referee approaches each player separately. It requests a choice: "even" or "odd". The player returns their choice.

**Important:** Players do not see the opponent's choice.

#### 3.2.4 Stage 4: Number Drawing

After receiving both choices, the Referee draws a number. The number is between 1 and 10. The drawing must be random.

#### 3.2.5 Stage 5: Winner Determination

The Referee checks:

- If the number is even and a player chose "even" – they win.
- If the number is odd and a player chose "odd" – they win.
- If both guessed correctly/incorrectly – draw.

#### 3.2.6 Stage 6: Result Reporting

The Referee sends:

1. GAME_OVER message to both players.
2. MATCH_RESULT_REPORT message to the League Manager.

### 3.3 Game States

The game transitions between defined states:

```
+---------------------+
| WAITING_FOR_PLAYERS |
+---------------------+
          |
          | Both players sent GAME_JOIN_ACK
          v
+---------------------+
| COLLECTING_CHOICES  |
+---------------------+
          |
          | Both players sent choose_parity
          v
+---------------------+
|   DRAWING_NUMBER    |
+---------------------+
          |
          | Result calculated
          v
+---------------------+
|      FINISHED       |
+---------------------+
```

#### 3.3.1 WAITING_FOR_PLAYERS State

The game starts in this state. The Referee waits for players to confirm arrival. Transition: When both players sent GAME_JOIN_ACK.

#### 3.3.2 COLLECTING_CHOICES State

The Referee collects choices from players. Transition: It occurs when both choices for choose_parity have been received.

#### 3.3.3 DRAWING_NUMBER State

The Referee draws a number and determines the winner. Transition: Automatic after calculation.

#### 3.3.4 FINISHED State

The game has ended. The result has been reported.

### 3.4 Scoring System

#### 3.4.1 Game Scoring

**Table 3: Scoring Table**

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

**Number of games in league:**
```
n(n-1) / 2
```

For 4 players: 4×3/2 = 6 games

#### 3.5.2 Example Game Schedule

**Table 4: Game Schedule for 4 Players**

| Match | Player A | Player B |
|-------|----------|----------|
| R1M1 | P01 | P02 |
| R1M2 | P03 | P04 |
| R2M1 | P01 | P03 |
| R2M2 | P02 | P04 |
| R3M1 | P01 | P04 |
| R3M2 | P02 | P03 |

### 3.6 Player Strategies

#### 3.6.1 Random Strategy

The simplest approach. The player randomly chooses "even" or "odd". The chance of winning is 50%.

**Random Strategy:**
```python
import random

def choose_parity_random():
    return random.choice(["even", "odd"])
```

#### 3.6.2 History-Based Strategy

The player remembers previous results. It attempts to identify patterns in draws.

**Note:** Since the draw is random, this strategy will not improve results in the long run.

#### 3.6.3 LLM-Guided Strategy

The player can use a language model. It builds a prompt and asks the model.

**Example prompt:**
```python
prompt = """
You are playing Even/Odd game.
Choose "even" or "odd".
Previous results: even won 3 times, odd won 2 times.
Your choice (one word only):
"""
```

**Note:** Using LLM is interesting but will not statistically improve performance. The game is a game of luck.

### 3.7 Game Rules Module

The rules module is a separate component in the Referee. It defines the specific logic for the game.

#### 3.7.1 Module Interface

The module provides functions:

- **init_game_state()** – Initialize game state.
- **validate_choice(choice)** – Check choice validity.
- **draw_number()** – Draw a number.
- **determine_winner(choices, number)** – Determine winner.

#### 3.7.2 Separation Advantage

In the future, the module can be replaced. Instead of Even/Odd, it's possible to use:

- Tic-Tac-Toe.
- 21 Questions.
- Memory game.

Only the rules module changes. The general protocol remains the same.

---

## 4. JSON Message Structures

This chapter defines all protocol messages. **Very Important:** All students must use exactly these structures. This will allow your agents to communicate with each other.

### 4.1 League Registration Messages

#### 4.1.1 LEAGUE_REGISTER_REQUEST – Registration Request

A player sends this request to the League Manager.

**League Registration Request:**
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

**Required fields:**

- **display_name** – Player's display name.
- **version** – Agent version.
- **game_types** – List of supported games.
- **contact_endpoint** – Player's server address.

#### 4.1.2 LEAGUE_REGISTER_RESPONSE – Registration Response

The League Manager returns this response.

**League Registration Response:**
```json
{
    "message_type": "LEAGUE_REGISTER_RESPONSE",
    "status": "ACCEPTED",
    "player_id": "P01",
    "reason": null
}
```

**Fields:**

- **status** – "ACCEPTED" or "REJECTED".
- **player_id** – Identifier assigned to player (only if accepted).
- **reason** – Rejection reason (only if rejected).

### 4.2 Round Messages

#### 4.2.1 ROUND_ANNOUNCEMENT – Round Announcement

The League Manager sends before each round.

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

### 4.3 Game Messages

#### 4.3.1 GAME_INVITATION – Game Invitation

The Referee sends to each player.

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

#### 4.3.2 GAME_JOIN_ACK – Arrival Confirmation

The player confirms receipt of the invitation.

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

### 4.4 Even/Odd Game Choice Messages

#### 4.4.1 CHOOSE_PARITY_CALL – Choice Request

The Referee requests the player to choose.

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

#### 4.4.2 CHOOSE_PARITY_RESPONSE – Choice Response

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

### 4.5 Result Messages

#### 4.5.1 GAME_OVER – Game End

The Referee sends to both players.

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

Possible values for status:

- **"WIN"** – There is a winner.
- **"DRAW"** – Draw.
- **"TECHNICAL_LOSS"** – Technical loss (response time, etc.).

#### 4.5.2 MATCH_RESULT_REPORT – Result Report to League

The Referee sends to the League Manager.

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

### 4.6 Standings Messages

#### 4.6.1 LEAGUE_STANDINGS_UPDATE – Standings Update

The League Manager sends to all players.

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

### 4.7 Message Summary Table

**Table 5: Summary of All Message Types**

| Message Type | Sender | Receiver | Purpose |
|--------------|--------|----------|---------|
| REGISTER_REQUEST | Player | League | League registration |
| REGISTER_RESPONSE | League | Player | Registration confirmation |
| ROUND_ANNOUNCEMENT | League | Players | Round publication |
| GAME_INVITATION | Referee | Player | Game invitation |
| GAME_JOIN_ACK | Player | Referee | Arrival confirmation |
| CHOOSE_PARITY_CALL | Referee | Player | Choice request |
| CHOOSE_PARITY_RESPONSE | Player | Referee | Choice response |
| GAME_OVER | Referee | Players | Game end |
| MATCH_RESULT_REPORT | Referee | League | Result report |
| STANDINGS_UPDATE | League | Players | Standings update |

### 4.8 Important Rules

#### 4.8.1 Required Fields

Every message must include:

- **message_type** – Always.
- **match_id** – In game messages.
- **player_id** – In player messages.

#### 4.8.2 Allowed Values

- **parity_choice:** Only "even" or "odd" (lowercase letters).
- **status:** Only "WIN", "DRAW", or "TECHNICAL_LOSS".
- **accept:** Only true or false (boolean).

#### 4.8.3 Time Format

All timestamps in ISO-8601 format:

```
YYYY-MM-DDTHH:MM:SSZ
```

**Example:** 2025-01-15T10:30:00Z

---

## 5. Implementation Guide

This chapter presents how to implement the agents. The examples are in Python with FastAPI. You can use any language that supports HTTP.

### 5.1 General Architecture

#### 5.1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator / Host                       │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ HTTP               │ HTTP               │ HTTP
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ League Manager  │  │     Referee     │  │     Players     │
│     :8000       │  │     :8001       │  │   :8101-8104    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

#### 5.1.2 Orchestrator Role

The Orchestrator coordinates between all agents:

- Sends HTTP requests to each server.
- Receives responses and processes them.
- Manages the league flow.

### 5.2 Simple MCP Server Implementation

#### 5.2.1 Basic Structure - FastAPI

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

A Player Agent must implement the following tools:

1. **handle_game_invitation** – Receiving game invitation.
2. **choose_parity** – Choosing "even" or "odd".
3. **notify_match_result** – Receiving game result.

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

The Referee must implement:

1. **start_match** – Starting a new game.
2. **collect_choices** – Collecting choices from players.
3. **draw_number** – Drawing a number.
4. **finalize_match** – Ending the game and reporting.

#### 5.4.2 Winner Determination Logic

**Winner Determination in Even/Odd Game:**
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

The League Manager must implement:

1. **register_player** – Registering a new player.
2. **create_schedule** – Creating the game schedule.
3. **report_match_result** – Receiving result reports.
4. **get_standings** – Returning the standings table.

#### 5.5.2 Game Schedule Creation

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

#### 5.6.1 Calling an MCP Tool

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

The player can store internal information:

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

#### 5.8.2 Response to Errors

If a player doesn't respond:

1. The Referee waits until timeout.
2. If no response – technical loss.
3. The Referee reports to the League Manager.

### 5.9 Local Testing

#### 5.9.1 Local Execution

Run each agent in a separate terminal:

**Running the Agents:**
```bash
# Terminal 1: League Manager
python league_manager.py  # Port 8000

# Terminal 2: Referee
python referee.py  # Port 8001

# Terminal 3-6: Players
python player.py --port 8101
python player.py --port 8102
python player.py --port 8103
python player.py --port 8104
```

#### 5.9.2 Connection Testing

**Server Testing:**
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

### 5.10 Implementation Tips

1. **Start simple** – First implement a random strategy.
2. **Test locally** – Run a league with yourselves.
3. **Save logs** – Document every message.
4. **Handle errors** – Use try/except.
5. **Follow the protocol** – Use JSON structures exactly.

---

## 6. Homework Requirements

### 6.1 Exercise Goal

In this exercise, you will implement a Player Agent for the Even/Odd league. Your agent will compete against agents of other students.

**Very Important:** Use exactly the protocol defined in this document. Otherwise, your agent will not be able to communicate with others.

### 6.2 Required Tasks

#### 6.2.1 Task 1: Player Agent Implementation

Implement an MCP server that listens on a port on localhost. The server must support the following tools:

1. **handle_game_invitation** – Receiving game invitation and returning GAME_JOIN_ACK.
2. **choose_parity** – Choosing "even" or "odd" and returning CHOOSE_PARITY_RESPONSE.
3. **notify_match_result** – Receiving game result and updating internal state.

#### 6.2.2 Task 2: League Registration

The agent must send a registration request to the League Manager. The request should include:

- Unique display name (your name or nickname).
- Agent version.
- Endpoint address of the server.

#### 6.2.3 Task 3: Self-Testing

Before submission, test your agent:

1. Run a local league with 4 players.
2. Ensure the agent responds to every message type.
3. Ensure JSON structures match the protocol.

### 6.3 Technical Requirements

#### 6.3.1 Programming Language

You can choose any language you want. The main thing is that the agent:

- Implements an HTTP server.
- Responds to POST requests at the `/mcp` path.
- Returns JSON in JSON-RPC 2.0 format.

#### 6.3.2 Response Times

- GAME_JOIN_ACK – within 5 seconds.
- CHOOSE_PARITY_RESPONSE – within 30 seconds.
- Any other response – within 10 seconds.

#### 6.3.3 Stability

The agent must:

- Operate without crashes.
- Handle input errors.
- Not stop operating in the middle of the league.

### 6.4 Work Process

#### 6.4.1 Stage 1: Local Development

1. Implement the agent.
2. Test locally with your code.
3. Fix bugs.

#### 6.4.2 Stage 2: Private League

1. Run a local league with 4 copies of the agent.
2. Verify all communication works.
3. Improve strategy (optional).

#### 6.4.3 Stage 3: Class League

1. Submit the agent.
2. The agent will run on the class server.
3. It will play against agents of other students.

### 6.5 Submission

#### 6.5.1 Files for Submission

1. Agent source code.
2. README file with running instructions.
3. Short report (1-2 pages) including:
   - Strategy description.
   - Difficulties encountered.
   - Conclusions from the exercise.

#### 6.5.2 Submission Format

- Single ZIP file.
- File name: HW_EvenOdd_<ID>.zip
- Replace <ID> with your ID number.

### 6.6 Grading Criteria

**Table 6: Grade Breakdown**

| Criterion | Description | Points |
|-----------|-------------|--------|
| Basic Functionality | Agent works, responds to messages, plays games | 30 |
| Protocol Compliance | JSON structures match protocol exactly | 20 |
| Stability | Agent is stable, doesn't crash, handles errors | 15 |
| Code Quality | Clean, documented, organized code | 15 |
| Documentation | Clear running instructions, detailed description | 10 |
| Strategy Bonus | Implementing an interesting strategy (not just random) | 10 |

### 6.7 Frequently Asked Questions

#### 6.7.1 Can I use external libraries?

Yes. You can use any library you want. Make sure you provide installation instructions.

#### 6.7.2 Must I use Python?

No. Use any language that suits you. The main thing is that the agent meets protocol requirements.

#### 6.7.3 What happens if my agent crashes?

The agent will suffer a technical loss in the current game. If it doesn't return to operation – it's out of the league.

#### 6.7.4 Can I update the agent after submission?

No. The submission is final. Test well before submitting.

#### 6.7.5 How do I know my standings?

The standings table will be published after each round. You'll be able to see your agent's position.

### 6.8 Summary

1. Implement a Player Agent that meets the protocol.
2. Test locally before submission.
3. Submit the code and report.
4. Your agent will play in the class league.

Good luck!

**Additional Information:**

For questions and clarifications, contact Dr. Yoram Segal.

It is recommended to read the book "AI Agents with MCP" [1].

For additional details about the MCP protocol, see the official documentation [2].

---

## 7. Learning MCP Through the League Exercise

The Even/Odd League exercise is not just a programming exercise. It serves as a complete pedagogical model for understanding the MCP protocol and AI agent principles. This chapter explains how the exercise teaches the foundational principles of AI agents and the MCP protocol.

### 7.1 The Player as an AI Agent

#### 7.1.1 Is the Player Agent an AI Agent?

The first question to ask is: Is the Player Agent in the league really an AI Agent? The answer is unequivocal: Yes.

An AI Agent is defined as an entity that performs interaction with the environment in order to achieve defined goals [1]. Unlike a regular program that executes predetermined instructions, an AI Agent is autonomous software that receives information from the environment, processes it, and decides by itself what to do based on the current state.

#### 7.1.2 The Four Characteristics of an AI Agent

Let's examine the Player Agent in the league in light of the four main characteristics of an AI Agent:

1. **Autonomy** – The agent operates independently. In the game context, the Player Agent decides autonomously which strategy to choose: "even" or "odd". No one tells it what to choose.

2. **Perception** – The agent absorbs information from the environment. The player absorbs game invitation messages (GAME_INVITATION), parity choice requests (CHOOSE_PARITY_CALL), and game results (GAME_OVER) from the Referee and League Manager.

3. **Action** – The agent affects the environment. The player performs actions by sending choices (CHOOSE_PARITY_RESPONSE) and arrival confirmations (GAME_JOIN_ACK) to games.

4. **Goal-orientation** – It has a defined goal. Its goal is to play, win games, and update its internal state such as win and loss history.

The Player Agent can even use a large language model (LLM) as a "brain" to choose the best strategy. In doing so, it demonstrates "thinking" or "inference" before action execution.

### 7.2 The Player in MCP Architecture

#### 7.2.1 Server or Client?

In the Even/Odd League architecture, the player is primarily an **MCP Server**.

An MCP Server is a component that exposes services and capabilities called "Tools", "Resources", or "Prompts". The server is defined as a separate process that operates on a defined port and provides a "gateway" to the external world [2].

The Player Agent is required to implement an HTTP server that receives POST requests at the `/mcp` path. The tools it exposes are called via JSON-RPC 2.0 protocol. Tools the player must implement include:

- **handle_game_invitation** – Handling game invitation.
- **choose_parity** – Choosing "even" or "odd".
- **notify_match_result** – Receiving notification about game result.

#### 7.2.2 Relationship with Referee and League Manager

Given that the player is the server exposing its services, the Client in the league system is whoever calls its services. The Referee and League Manager act as clients or Orchestrators.

The Referee is the orchestrator that acts as an MCP Client and calls the player's choose_parity tool. When the Referee wants to collect choices from players, it sends a request creating CHOOSE_PARITY_CALL to each player's choose_parity tool.

**In summary:** Although the Player Agent is an autonomous AI Agent, from an MCP protocol implementation perspective, it fulfills the server role that offers capabilities to the central orchestrators.

### 7.3 Referee and League Manager as AI Agents

#### 7.3.1 Higher-Level Agents

The Referee and League Manager are also defined as AI Agents. They meet the same four characteristics:

**Table 7: AI Agent Characteristics for Referee and League Manager**

| Characteristic | League Manager | Referee |
|----------------|----------------|---------|
| Goal-orientation | Managing entire league, creating game schedule, calculating standings | Managing single game, validating move legality, determining winner |
| Autonomy | Operates independently for determining game rounds | Manages game stages: invitation, choice collection, drawing |
| Perception | Absorbs registration requests from players, result reports from referees | Absorbs arrival confirmations, parity choices from players |
| Action | Sends round announcements, updates standings tables | Sends game invitations, choice requests, reports results |

These agents are not passive. They manage the entire system according to rules and fixed goals. This is the essence of goal-orientation and autonomy of an AI Agent.

#### 7.3.2 MCP Servers That Also Act as Clients

Both of these agents are also defined as MCP servers:

- The League Manager operates as an MCP server on port 8000. It implements tools like register_player, start_match, and report_match_result.
- The Referee operates as an MCP server on port 8001. It implements tools like start_match and collect_choices.

**Important note:** Although they are defined as servers, the Referee and League Manager must also act as MCP Clients to fulfill their central role. For example:

- The Referee must act as a client to call the player agent's choose_parity tool.
- The League Manager must act as a client to send round announcements to the player agents.

In this system, the central servers are actually orchestrator-clients that need to initiate action at the player servers.

### 7.4 Central Insight: Role Reversal

#### 7.4.1 The Traditional Paradigm

In typical client-server architecture, the client is the active component that sends requests, and the server is the passive component that waits for requests.

#### 7.4.2 Role Reversal in the AI League

In the AI league, a creative role reversal occurs:

**The player (autonomous agent) is the server:** Although the player is the autonomous entity that needs to perform action, it is required to expose its capabilities as an MCP server.

**The Referee and League Manager (orchestrators) are the clients:** The Referee is the orchestrator that acts as an MCP Client and calls the player's choose_parity tool to initiate the next move in the game.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Referee (Orchestrator)                                  │
│                     Acts as MCP Client                                      │
│                          :8001                                              │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                              │
         │ choose_parity                                │ choose_parity
         ▼                                              ▼
┌─────────────────────┐                      ┌─────────────────────┐
│     Player 1        │                      │     Player 2        │
│   (MCP Server)      │                      │   (MCP Server)      │
│      :8101          │                      │      :8102          │
└─────────────────────┘                      └─────────────────────┘
                                    
                                    ▲
                                    │
                                    │ ROUND_ANNOUNCEMENT
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                     League Manager                                          │
│                     Acts as MCP Client                                      │
│                          :8000                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.5 Layer Separation Principle

#### 7.5.1 Three Separate Layers

The MCP protocol enables clear separation between roles:

1. **League Layer** (managed by League Manager) – Player recruitment, Round-Robin game schedule, and standings table.

2. **Refereeing Layer** (managed by Referee) – Single game management and move validation.

3. **Game Rules Layer** (managed by separate module) – Specific logic for Even/Odd game.

#### 7.5.2 The Advantage of Separation

By exposing an MCP interface (standard JSON-RPC 2.0 over HTTP), the player allows the league to remain agnostic to the development language or internal strategy.

This is a solution to the fragmentation problem where every agent and every model previously required unique integration. The MCP protocol solves this by creating a universal interface [2].

When the player receives a request like CHOOSE_PARITY_CALL, the data comes in a fixed JSON structure. The player responds with CHOOSE_PARITY_RESPONSE, also in a fixed structure. This ensures that every agent, regardless of how it computes the data, can communicate consistently with any other orchestrator that respects the protocol.

### 7.6 The Role of LLM in the Server Agent

#### 7.6.1 The Dilemma

An interesting question arises: On one hand, the player is defined as an MCP Server that exposes capabilities. On the other hand, it's described as an autonomous AI Agent that can use an LLM as a "brain" for strategy selection. In traditional definitions, a server doesn't invoke a "brain" but rather fulfills a request.

#### 7.6.2 The Solution: Role Separation

The solution lies in understanding that MCP roles (server/client) and AI components (brain/tools) are separate but complementary concepts.

**The agent is both server and client (in practice):** Each of the agents is actually both server and client. The server role is required for each agent to host itself so others can call its tools. The client role is required for any agent that needs to initiate interaction.

**LLM as Internal Component:** The large language model is simply an internal component within the agent's general loop. If the Player Agent implements choose_parity, when the server receives the request:

1. The MCP layer (server) absorbs the request.
2. The agent's internal logic (LLM or other strategy) is activated for determining the choice.
3. The MCP layer (server) sends back the response.

The central idea in MCP is that even when the "brain" is inside the server, external communication will remain standard via JSON-RPC. The LLM is the "intelligence" of the server, and it doesn't violate the client-server model.

#### 7.6.3 Analogy: Customer Service Station

The architecture can be imagined as a customer service station:

- **MCP (Protocol)** – is the phone and language they speak (JSON-RPC over HTTP).
- **Player (Server)** – is the service office with its own phone booth.
- **Strategy/LLM (Brain)** – is the smart advisor sitting inside the office, receiving the call, computing the answer, and dictating to the MCP layer what response to send back.
- **Internal Tools** (LLM and logic) are not directly exposed to the MCP protocol, but serve the public tools the agent exposes, such as choose_parity.

### 7.7 The Orchestrator Role

#### 7.7.1 League Manager – The Architect

The League Manager is the highest-level AI Agent strategically, managing the league layer. It is not involved in the game rules themselves, but in general management: game schedule and standings table.

**Advantage of Separation:** If the league wanted to replace the game from Even/Odd to Tic-Tac-Toe, the League Manager would change hardly at all. This is a perfect demonstration of the role separation principle promoted by MCP.

#### 7.7.2 The Referee – The Dynamic Implementer

The Referee embodies the refereeing layer. It doesn't know the game rules (which are handled by a separate module), but rather is responsible for managing the Conversation Lifecycle between players.

The Referee ensures players meet response deadlines. It is the one that activates the external agent loop for the players – it calls their choose_parity tool and thereby initiates the player's autonomous action.

**MCP enables clear role division:** The Referee and League Manager are responsible for "how" (protocol and communication), while the players are responsible for "what" (content and strategy).

### 7.8 What the Exercise Teaches

#### 7.8.1 Foundational Principles of AI Agents

The exercise teaches the four characteristics of an AI Agent practically:

- **Autonomy** – The player decides by itself.
- **Perception** – The player absorbs messages from the system.
- **Action** – The player sends responses.
- **Goal-orientation** – The player strives to win.

#### 7.8.2 Foundational Principles of MCP

The exercise teaches the core principles of MCP protocol:

1. **Standard Interface** – Each agent exposes tools via JSON-RPC 2.0.
2. **Role Separation** – League layer, refereeing layer, and game rules layer.
3. **Language Agnostic** – Can implement agent in any programming language.
4. **Communication Through Orchestrator** – Agents don't talk directly, but through Referee or League Manager.

#### 7.8.3 The Learning Experience

At the end of the exercise, the student will understand:

- How an AI Agent communicates with other agents.
- How to build a simple MCP server.
- What "Tools" mean in the MCP protocol.
- How an orchestrator manages interaction between agents.
- Why layer separation is important for AI system design.

### 7.9 Summary

The Even/Odd League exercise serves as a perfect pedagogical model for understanding the MCP protocol and AI agents. The simple game allows focusing on architectural principles without getting entangled in complex logic.

The student learns that an AI Agent can also be an MCP Server – a creative role reversal that allows orchestrators to call agents and initiate their action. The layer separation ensures that the league game can be replaced in the future without changing the general protocol.

For additional details about the MCP protocol, see the book "AI Agents with MCP" [1] and Anthropic's official documentation [2].

---

## 8. References

1. Y. Segal, *AI Agents with MCP*. Dr. Yoram Segal, 2025, Hebrew edition.

2. Anthropic, *Model context protocol specification*, 2024. [Online]. Available: https://modelcontextprotocol.io/

3. JSON-RPC Working Group, *JSON-RPC 2.0 specification*, 2010. [Online]. Available: https://www.jsonrpc.org/specification

4. K. Stratis, *AI Agents with MCP*. O'Reilly Media, 2025, Early Release.

---

© Dr. Yoram Segal - All Rights Reserved
