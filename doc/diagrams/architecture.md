# Architecture Diagrams

## System Overview

```mermaid
graph TB
    subgraph "League System Architecture"
        LM[League Manager<br/>Port: 8000]
        R1[Referee 1<br/>Port: 8001]
        R2[Referee 2<br/>Port: 8002]
        P1[Player 1<br/>Port: 8101]
        P2[Player 2<br/>Port: 8102]
        P3[Player 3<br/>Port: 8103]
        P4[Player 4<br/>Port: 8104]
    end
    
    subgraph "SDK Layer"
        SDK[league_sdk<br/>- Config<br/>- Logging<br/>- MCP Client/Server<br/>- Game Rules]
    end
    
    P1 -->|HTTP POST /mcp| LM
    P2 -->|HTTP POST /mcp| LM
    P3 -->|HTTP POST /mcp| LM
    P4 -->|HTTP POST /mcp| LM
    
    R1 -->|Report Results| LM
    R2 -->|Report Results| LM
    
    LM -->|Start Match| R1
    LM -->|Start Match| R2
    
    R1 -->|Invite/Call| P1
    R1 -->|Invite/Call| P2
    R2 -->|Invite/Call| P3
    R2 -->|Invite/Call| P4
    
    LM -.->|Uses| SDK
    R1 -.->|Uses| SDK
    R2 -.->|Uses| SDK
    P1 -.->|Uses| SDK
    P2 -.->|Uses| SDK
    P3 -.->|Uses| SDK
    P4 -.->|Uses| SDK
```

## Three-Layer Architecture

```mermaid
graph TD
    subgraph "Layer 1: League Management"
        LM[League Manager]
        LM_REG[Registration]
        LM_SCHED[Scheduling]
        LM_STAND[Standings]
    end
    
    subgraph "Layer 2: Game Refereeing"
        REF[Referee Agent]
        REF_INV[Invitations]
        REF_MOVES[Move Collection]
        REF_RESULT[Result Reporting]
    end
    
    subgraph "Layer 3: Game Rules"
        GAME[EvenOddGame]
        GAME_DRAW[Number Drawing]
        GAME_WIN[Winner Determination]
    end
    
    LM --> LM_REG
    LM --> LM_SCHED
    LM --> LM_STAND
    
    REF --> REF_INV
    REF --> REF_MOVES
    REF --> REF_RESULT
    
    GAME --> GAME_DRAW
    GAME --> GAME_WIN
    
    LM -->|Assign Matches| REF
    REF -->|Use Rules| GAME
```

## Registration Flow

```mermaid
sequenceDiagram
    participant R as Referee
    participant LM as League Manager
    participant P1 as Player 1
    participant P2 as Player 2
    
    Note over R,P2: Stage 1: Referee Registration (V2)
    R->>LM: REFEREE_REGISTER_REQUEST
    LM->>LM: Generate referee_id + auth_token
    LM-->>R: REFEREE_REGISTER_RESPONSE<br/>{referee_id, auth_token}
    
    Note over P1,P2: Stage 2: Player Registration
    P1->>LM: LEAGUE_REGISTER_REQUEST<br/>{protocol: "league.v2"}
    LM->>LM: Validate version ≥2.0.0
    LM->>LM: Generate player_id + auth_token
    LM-->>P1: LEAGUE_REGISTER_RESPONSE<br/>{player_id: "P01", auth_token}
    
    P2->>LM: LEAGUE_REGISTER_REQUEST
    LM-->>P2: LEAGUE_REGISTER_RESPONSE<br/>{player_id: "P02", auth_token}
    
    Note over LM: After 60s timeout
    LM->>LM: Close registration<br/>Generate schedule
```

## Match Execution Flow

```mermaid
sequenceDiagram
    participant LM as League Manager
    participant REF as Referee
    participant PA as Player A
    participant PB as Player B
    
    LM->>REF: start_match(match_details)
    
    par Send Invitations
        REF->>PA: GAME_INVITATION
        REF->>PB: GAME_INVITATION
    end
    
    par Collect Join ACKs
        PA-->>REF: GAME_JOIN_ACK
        PB-->>REF: GAME_JOIN_ACK
    end
    
    par Request Parity Choices
        REF->>PA: CHOOSE_PARITY_CALL
        REF->>PB: CHOOSE_PARITY_CALL
    end
    
    par Collect Choices
        PA-->>REF: CHOOSE_PARITY_RESPONSE<br/>{"even"}
        PB-->>REF: CHOOSE_PARITY_RESPONSE<br/>{"odd"}
    end
    
    REF->>REF: Draw random number (1-10)
    REF->>REF: Determine winner
    
    par Send Results
        REF->>PA: GAME_OVER {winner, score}
        REF->>PB: GAME_OVER {winner, score}
    end
    
    REF->>LM: MATCH_RESULT_REPORT
    
    LM->>LM: Update standings
    
    alt Round Complete
        par Notify All Players
            LM->>PA: STANDINGS_NOTIFICATION
            LM->>PB: STANDINGS_NOTIFICATION
        end
    end
```

## SDK Module Structure

```mermaid
graph LR
    subgraph "league_sdk Package"
        INIT[__init__.py]
        
        subgraph "Configuration"
            CFG_MODEL[config_models.py]
            CFG_LOAD[config_loader.py]
        end
        
        subgraph "Data Access"
            REPOS[repositories.py]
        end
        
        subgraph "Protocol"
            SCHEMA[schemas.py]
            HELPERS[helpers.py]
        end
        
        subgraph "MCP"
            MCP_CLIENT[mcp_client.py]
            MCP_SERVER[mcp_server.py]
        end
        
        subgraph "Logging"
            LOGGER[logger.py]
        end
        
        subgraph "Game Rules"
            GAME_INIT[game_rules/__init__.py]
            EVEN_ODD[game_rules/even_odd.py]
        end
    end
    
    INIT --> CFG_LOAD
    INIT --> SCHEMA
    INIT --> MCP_CLIENT
    INIT --> MCP_SERVER
    INIT --> LOGGER
    INIT --> REPOS
    
    CFG_LOAD --> CFG_MODEL
    MCP_SERVER --> SCHEMA
    MCP_CLIENT --> SCHEMA
    REPOS --> CFG_LOAD
    LOGGER --> HELPERS
```

## Agent Modular Structure

```mermaid
graph TD
    subgraph "League Manager"
        LM_MAIN[main.py<br/>Entry point]
        LM_HAND[handlers.py<br/>Message handling]
        LM_SCHED[scheduler.py<br/>Round management]
    end
    
    subgraph "Referee Template"
        REF_MAIN[main.py<br/>Entry point]
        REF_HAND[handlers.py<br/>Message handling]
        REF_LOGIC[game_logic.py<br/>Match execution]
    end
    
    subgraph "Player Template"
        PL_MAIN[main.py<br/>Entry point]
        PL_HAND[handlers.py<br/>Message handling]
        PL_STRAT[strategy.py<br/>Playing strategy]
    end
    
    LM_MAIN --> LM_HAND
    LM_MAIN --> LM_SCHED
    LM_HAND --> SDK
    LM_SCHED --> SDK
    
    REF_MAIN --> REF_HAND
    REF_MAIN --> REF_LOGIC
    REF_HAND --> SDK
    REF_LOGIC --> SDK
    
    PL_MAIN --> PL_HAND
    PL_MAIN --> PL_STRAT
    PL_HAND --> SDK
    PL_STRAT --> SDK
    
    SDK[league_sdk]
```

## Query Flow (LEAGUE_QUERY)

```mermaid
sequenceDiagram
    participant P as Player
    participant LM as League Manager
    
    Note over P,LM: Get Current Standings
    P->>LM: LEAGUE_QUERY<br/>{query_type: "GET_STANDINGS",<br/>auth_token}
    LM->>LM: Validate auth_token
    LM->>LM: Calculate current standings
    LM-->>P: LEAGUE_QUERY_RESPONSE<br/>{success: true, data: {standings}}
    
    Note over P,LM: Get Next Match
    P->>LM: LEAGUE_QUERY<br/>{query_type: "GET_NEXT_MATCH",<br/>params: {player_id: "P01"}}
    LM->>LM: Find next uncompleted match
    LM-->>P: LEAGUE_QUERY_RESPONSE<br/>{success: true,<br/>data: {match_id, opponent_id}}
```
