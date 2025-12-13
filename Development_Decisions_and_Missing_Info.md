# Development Decisions and Missing Information Log
## Even/Odd AI Agent League System

**Document Purpose:** Track all missing data, ambiguities in requirements, and critical design decisions made during development.

**Version:** 1.0  
**Date:** December 2025  
**Project:** Even/Odd League (Homework 07)

---

## Table of Contents

1. [Missing Information from Requirements](#1-missing-information-from-requirements)
2. [Ambiguities Requiring Clarification](#2-ambiguities-requiring-clarification)
3. [Design Decisions Made](#3-design-decisions-made)
4. [Technical Implementation Decisions](#4-technical-implementation-decisions)
5. [Testing and Validation Decisions](#5-testing-and-validation-decisions)
6. [Deployment Decisions](#6-deployment-decisions)
7. [Open Questions for User](#7-open-questions-for-user)

---

## 1. Missing Information from Requirements

### 1.1 Orchestrator Implementation Details

**What's Missing:**
- Exact implementation of the Orchestrator/Host component
- Whether Orchestrator should be a separate script or integrated into League Manager
- Orchestrator's state management approach
- Error recovery strategy when Orchestrator crashes

**Impact on Development:**
- Critical for system startup and coordination
- Affects testing procedures
- Determines who initiates MCP handshakes

**✅ FINAL DECISION:**
- **Orchestrator is integrated into League Manager and Referee** (not a separate component)
- League Manager acts as high-level orchestrator for the entire league
- Referee acts as match-level orchestrator for individual games
- Each component handles its own orchestration responsibilities

**Implementation:**
- League Manager: Orchestrates player registration, schedule creation, and standings
- Referee: Orchestrates match execution (invitations, choice collection, result reporting)
- No separate orchestrator.py needed

**Rationale:**
- Simplifies deployment (fewer components to manage)
- Natural responsibility assignment (each orchestrates its domain)
- Referee is the orchestrator at match level, League Manager at league level

---

### 1.2 MCP Handshake Initialization

**What's Missing:**
- Who initiates MCP `initialize` handshake with whom?
- Do Player Agents need to send `initialize` to League Manager on startup?
- Or does Orchestrator handle all initialization?
- What happens if a player connects mid-league?

**Impact on Development:**
- Affects startup sequence
- Determines connection lifecycle management
- Impacts auto-discovery vs. pre-configuration

**✅ FINAL DECISION: Option B - Player Self-Registration**
- **Players register themselves** by calling League Manager's `register_player` tool
- League Manager waits for player registrations for a **configurable time period**
- Default wait time: **1 minute** (if not specified in configuration)
- Wait time should be specified in configuration file

**Registration Flow:**
1. League Manager starts and enters REGISTRATION state
2. League Manager waits for registration period (configurable, default 60 seconds)
3. Players start up and call `register_player` tool on League Manager
4. League Manager assigns player_id and confirms
5. After registration period ends, League Manager proceeds to schedule creation

**Configuration:**
```yaml
league:
  registration_timeout_seconds: 60  # Default if not specified
```

**Mid-League Connection:**
- Players connecting after registration period closes are **rejected**
- League Manager returns status: "REJECTED", reason: "Registration closed"

**Rationale:**
- Players are autonomous agents - they should initiate their own registration
- Configurable timeout provides flexibility for different deployment scenarios
- Clear registration window prevents complications during active league

---

### 1.3 Authentication and Security

**What's Missing:**
- No mention of authentication between agents
- No API keys or tokens defined
- How to prevent malicious agents in class league?
- Rate limiting to prevent DoS attacks?

**Impact on Development:**
- Security risk in multi-machine deployment
- Could allow cheating or disruption in class league

**✅ FINAL DECISION:**
- **No authentication required** for current implementation
- All communication is in trusted environment
- No tokens, API keys, or validation needed

**Rationale:**
- Simplifies implementation and testing
- Sufficient for educational/development purposes
- Can be added later if deployment requirements change

---

### 1.4 Game Draw Seeding

**What's Missing:**
- Should random number draws be seeded for reproducibility?
- Who controls the random seed (referee or orchestrator)?
- Should draws be logged for audit trail?

**Impact on Development:**
- Affects testing reproducibility
- Important for debugging and dispute resolution

**Proposed Decision:**
- Referee uses `random.SystemRandom()` for cryptographically secure randomness (no seed)
- Each draw is logged with timestamp
- Draw logs stored in `match_history.json` for audit

**Rationale:**
- Ensures fairness (no predictable patterns)
- Logging enables dispute resolution
- Testing can mock random for determinism

---

### 1.5 Persistence and Recovery

**What's Missing:**
- What happens if League Manager crashes mid-league?
- Should standings be persisted to disk?
- Recovery strategy for incomplete matches?

**Impact on Development:**
- Data loss risk
- Affects long-running leagues
- Important for class league (hours of execution)

**Proposed Decision:**
- **League Manager:** Persist to `league_state.json` after every match result
- **Referee:** Stateless per-match (no persistence needed)
- **Players:** Optional (for learning strategies)

**Recovery Protocol:**
```
1. On League Manager restart:
   - Load league_state.json
   - Resume from last completed match
   - Re-announce current round
   
2. On Referee crash during match:
   - Orchestrator detects timeout
   - Marks match as "ABORTED"
   - Reschedules match at end of round
```

---

### 1.6 Concurrency and Parallelism

**What's Missing:**
- Can multiple matches run simultaneously?
- Single Referee vs. multiple Referee instances?
- Locking strategy for standings updates?

**Impact on Development:**
- Performance (sequential = slow)
- Complexity (parallel = race conditions)

**✅ FINAL DECISION: Parallel Match Execution**
- **Multiple matches run in parallel** using multiple Referee instances
- **For 4 players:** 2 Referees running simultaneously (2 concurrent matches)
- **Prepare code to scale up to 50 players**
- League Manager uses threading/async to handle concurrent standings updates

**Implementation Architecture:**
```python
# For 4 players: 6 total matches in Round-Robin
# Round 1: Match 1 (P01 vs P02) + Match 2 (P03 vs P04) - parallel
# Round 2: Match 3 (P01 vs P03) + Match 4 (P02 vs P04) - parallel  
# Round 3: Match 5 (P01 vs P04) + Match 6 (P02 vs P03) - parallel

# Each Referee handles one match independently
```

**Referee Scaling:**
- 4 players → 6 matches → 2 concurrent referees
- 10 players → 45 matches → 5 concurrent referees
- 50 players → 1,225 matches → 25 concurrent referees

**Standings Update Protection:**
```python
# In league_manager.py
import threading

standings_lock = threading.Lock()

def update_standings(match_result):
    with standings_lock:
        # Safe concurrent updates
        self.standings = recalculate_standings(match_result)
        self.save_to_disk()
```

**Rationale:**
- Dramatically reduces total league execution time
- 4 players: Sequential = 6 min, Parallel = 3 min
- 50 players: Sequential = ~20 hours, Parallel = ~1 hour
- Scales appropriately for larger leagues

---

## 2. Ambiguities Requiring Clarification

### 2.1 "Both Choose Same" Draw Logic

**Ambiguity:**
The requirements state: "If both chose the same thing and were right – tie. If both chose the same thing and were wrong – tie."

**Question:** Does this mean:
- **Interpretation A:** If both choose "even" and number is even → Tie (both correct)
- **Interpretation B:** If both choose "even" → Always Tie (regardless of number)?

**Requirements Quote:**
> "If both chose the same thing and both guessed correctly/incorrectly – draw."

**Clarification Needed:** This seems to suggest ANY same choice = draw.

**✅ CONFIRMED: Interpretation B (Any same choice = draw)**
- If both players choose the same option (both "even" or both "odd") → **ALWAYS DRAW**
- The drawn number is irrelevant when both choose the same
- This applies whether they would have both been right or both been wrong

**Rationale:**
- Simplifies implementation
- Matches example in assignment: "both chose 'even' and number is even – tie, both were right"
- Fair game mechanic (prevents both from winning)

**Implementation:**
```python
def determine_winner(choice_A, choice_B, drawn_number):
    if choice_A == choice_B:
        return "DRAW"  # Always draw if same choice
    
    parity = "even" if drawn_number % 2 == 0 else "odd"
    if choice_A == parity:
        return "PLAYER_A"
    else:
        return "PLAYER_B"
```

---

### 2.2 Retry vs. Technical Loss

**Ambiguity:**
Requirements mention "3 failed attempts → technical loss" for invalid moves. But also "30 second timeout → technical loss".

**Question:** Are these separate counters?
- If player sends invalid choice 2 times, then times out → which error triggers?

**✅ FINAL DECISION: Separate Tracking with Specific Timeouts**

**Timeout Specifications:**
- **GAME_JOIN_ACK:** Within **5 seconds**
- **CHOOSE_PARITY_RESPONSE:** Within **30 seconds**  
- **Any other response:** Within **10 seconds**

**Retry Mechanism:**
- Invalid responses trigger retry (up to 3 attempts total)
- Each retry attempt has the same timeout as original
- Between retries: wait, retry, wait, retry, etc.
- Timeout on ANY single attempt → Immediate technical loss (no retry)

**Algorithm:**
```python
MAX_RETRIES = 3
TIMEOUT_GAME_JOIN_ACK = 5  # seconds
TIMEOUT_CHOOSE_PARITY = 30  # seconds
TIMEOUT_OTHER = 10  # seconds

for attempt in 1..MAX_RETRIES:
    response = request_with_timeout(TIMEOUT_CHOOSE_PARITY)
    
    if timeout:
        return TECHNICAL_LOSS (reason: "timeout")
    
    if response.parity_choice in ["even", "odd"]:
        return response.parity_choice  # Valid choice
    
    # Invalid choice - send rejection and retry
    send_MOVE_REJECTED(reason="parity_choice must be 'even' or 'odd'")
    # Continue to next retry attempt

# All retries exhausted with invalid responses
return TECHNICAL_LOSS (reason: "3 invalid moves")
```

**Examples:**
1. **Timeout on first attempt:** Immediate technical loss, no retry
2. **Invalid move on attempt 1, timeout on attempt 2:** Technical loss (timeout)
3. **Invalid moves on attempts 1, 2, 3:** Technical loss (3 invalid moves)
4. **Invalid move on attempt 1, valid on attempt 2:** Success (choice accepted)

**Rationale:**
- Timeout indicates non-responsive player (hard failure)
- Invalid moves indicate protocol error (soft failure, allow correction)
- Separate handling provides fairness while maintaining performance

---

### 2.3 Standings Tie-Breaking

**Ambiguity:**
Requirements say:
> "Standings determined by: 1. Total points (descending), 2. Number of wins (descending), 3. Draw difference (descending)"

**Question:** What is "draw difference"?
- **Option A:** Draws won minus draws lost (doesn't make sense)
- **Option B:** Goal difference (not applicable to this game)
- **Option C:** Total draws (more draws = higher rank)

**✅ FINAL DECISION: Corrected Tie-Breaking Rules**

**Standings Ranking Order:**
1. **Total points** (descending) - 3 for win, 1 for draw, 0 for loss
2. **Number of wins** (descending)
3. **Number of ties/draws** (descending)

**Rationale:**
- Clear and unambiguous ranking
- Rewards more draws over losses when points are equal
- "Draw difference" was likely meant to be "Number of draws"

**Example Standings:**
```
Rank | Player | Points | Wins | Draws | Losses
-----|--------|--------|------|-------|--------
1    | P01    | 7      | 2    | 1     | 0      (2 wins, 1 draw)
2    | P02    | 7      | 2    | 1     | 0      (2 wins, 1 draw, same as P01)
3    | P03    | 4      | 1    | 1     | 1      
4    | P04    | 0      | 0    | 0     | 3
```
Note: P01 and P02 tied - would need 4th criterion (alphabetical by player_id) if head-to-head not applicable.

---

### 2.4 Message Type in Tools vs. Wrapper

**Ambiguity:**
Do tools receive the `message_type` field as part of their parameters?

**Example:**
```json
// Option A - message_type in parameters
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": {
      "message_type": "CHOOSE_PARITY_CALL",  // <-- here?
      "match_id": "R1M1",
      ...
    }
  }
}

// Option B - message_type outside MCP
{
  "protocol": "league.v1",
  "message_type": "CHOOSE_PARITY_CALL",  // <-- here?
  ...
}
```

**✅ FINAL DECISION: All Messages Include Complete Protocol Structure**

**Required Base Fields in ALL Messages:**
Every message in the protocol must include these base fields:
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

**Additional Required Fields:**

**For Game Messages** (add to base fields):
- `match_id` - MUST be included
- `round_id` - MUST be included

**For Player Messages** (add to base fields):
- `player_id` - MUST be included when message is directed to/from specific player

**Complete Example - CHOOSE_PARITY_CALL:**
```json
{
  "protocol": "league.v1",
  "message_type": "CHOOSE_PARITY_CALL",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "conversation_id": "conv-r1m1-001",
  "sender": "referee",
  "timestamp": "2025-01-15T10:30:00Z",
  "player_id": "P01",
  "game_type": "even_odd",
  "context": {
    "opponent_id": "P02",
    "your_standings": { ... }
  },
  "deadline": "2025-01-15T10:30:30Z"
}
```

**MCP Wrapper:**
These complete messages are then wrapped in JSON-RPC 2.0:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": { 
      /* Complete message with all base fields above */
    }
  },
  "id": 1
}
```

**Rationale:**
- Consistent message structure across all communication
- Every message is self-contained with full context
- Enables proper logging, tracing, and debugging
- Clear sender/receiver tracking via conversation_id

---

## 3. Design Decisions Made

### 3.1 JSON Schema Validation

**Decision:** Use `pydantic` for automatic JSON schema validation

**Rationale:**
- FastAPI integrates natively with Pydantic
- Automatic validation of input/output schemas
- Clear error messages for debugging
- Type safety in Python code

**Example:**
```python
from pydantic import BaseModel, Field

class GameInvitationRequest(BaseModel):
    message_type: str = Field(..., const="GAME_INVITATION")
    match_id: str
    game_type: str
    opponent_id: str
    
class GameJoinAckResponse(BaseModel):
    message_type: str = Field(..., const="GAME_JOIN_ACK")
    match_id: str
    player_id: str
    arrival_timestamp: str
    accept: bool = True
```

---

### 3.2 Async vs. Sync HTTP

**Decision:** Use `asyncio` and `httpx` for async HTTP calls

**Rationale:**
- Enables parallel match execution
- Non-blocking I/O during player calls
- Better resource utilization
- Scales to 100+ players

**Trade-off:**
- More complex code (async/await)
- Harder to debug
- Acceptable: Performance gain is critical for class league

---

### 3.3 Error Logging Strategy

**Decision:** Structured logging with JSON format

**Implementation:**
```python
import logging
import json

logging.basicConfig(
    filename="referee.log",
    level=logging.INFO,
    format='%(message)s'
)

def log_match_event(event_type, match_id, details):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "match_id": match_id,
        "details": details
    }
    logging.info(json.dumps(log_entry))
```

**Rationale:**
- Easy parsing for analysis
- Enables debugging complex issues
- Can replay matches from logs

---

### 3.4 Configuration Management

**Decision:** Centralized config file (`config.yaml`) for all endpoints

**Format:**
```yaml
league:
  league_id: "league_2025_even_odd"
  game_type: "even_odd"
  
agents:
  league_manager:
    host: "localhost"
    port: 8000
    endpoint: "/mcp"
    
  referee:
    host: "localhost"
    port: 8001
    endpoint: "/mcp"
    
  players:
    - id: "P01"
      host: "localhost"
      port: 8101
      strategy: "random"
    - id: "P02"
      host: "localhost"
      port: 8102
      strategy: "llm"
      llm_config:
        api_key_env: "GEMINI_API_KEY"
        model: "gemini-pro"
```

**Rationale:**
- Single source of truth
- Easy to switch between local/distributed
- Version control friendly

---

## 4. Technical Implementation Decisions

### 4.1 Game Rules Module Interface

**Decision:** Pluggable game rules via Python `Protocol`

**Implementation:**
```python
from typing import Protocol, Dict, Tuple

class GameRules(Protocol):
    def init_game_state(self) -> Dict:
        """Initialize empty game state"""
        ...
    
    def validate_move(self, state: Dict, player_id: str, move: Dict) -> Tuple[bool, str]:
        """Return (is_valid, error_message)"""
        ...
    
    def apply_move(self, state: Dict, move: Dict) -> Dict:
        """Return updated state"""
        ...
    
    def check_game_status(self, state: Dict) -> Dict:
        """Return {status: ONGOING|WIN|DRAW, winner: player_id}"""
        ...
```

**Usage in Referee:**
```python
from game_rules.even_odd import EvenOddRules

class RefereeAgent:
    def __init__(self, game_rules: GameRules):
        self.game_rules = game_rules
    
    def execute_match(self, match_id, player_A, player_B):
        state = self.game_rules.init_game_state()
        # ... rest of match logic
```

**Rationale:**
- Easy to add new games (Tic-Tac-Toe, etc.)
- Clear contract for game implementation
- Referee remains game-agnostic

---

### 4.2 LLM Integration (Gemini API)

**Decision:** Optional LLM strategy with fallback

**Implementation:**
```python
import os
import google.generativeai as genai
from typing import Optional

class LLMStrategy:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
        else:
            self.enabled = False
            logging.warning("GEMINI_API_KEY not set, using random strategy")
    
    def choose_parity(self, context: dict, history: list) -> str:
        if not self.enabled:
            return random.choice(["even", "odd"])
        
        try:
            prompt = self._build_prompt(context, history)
            response = self.model.generate_content(prompt)
            choice = self._parse_response(response.text)
            return choice
        except Exception as e:
            logging.error(f"LLM call failed: {e}, using random fallback")
            return random.choice(["even", "odd"])
    
    def _parse_response(self, text: str) -> str:
        text = text.strip().lower()
        if "even" in text:
            return "even"
        elif "odd" in text:
            return "odd"
        else:
            return "even"  # Safe default
```

**Rationale:**
- Graceful degradation if API unavailable
- Prevents homework deadline issues (API outages)
- Demonstrates LLM integration without being mandatory

---

### 4.3 Database vs. File Storage

**Decision:** JSON files for simplicity

**Structure:**
```
data/
├── league_state.json       # League Manager state
├── match_history.json      # All completed matches
├── player_registry.json    # Registered players
└── logs/
    ├── league_manager.log
    ├── referee.log
    └── player_P01.log
```

**Rationale:**
- Simple implementation (no SQL setup)
- Human-readable for debugging
- Sufficient for homework scale (4-30 players)

**Future:** For 1000+ players, migrate to PostgreSQL or MongoDB.

---

## 5. Testing and Validation Decisions

### 5.1 Unit Test Framework

**Decision:** `pytest` with fixtures

**Example:**
```python
# tests/test_referee.py
import pytest
from referee_agent import RefereeAgent
from game_rules.even_odd import EvenOddRules

@pytest.fixture
def referee():
    return RefereeAgent(game_rules=EvenOddRules())

def test_determine_winner_both_even(referee):
    result = referee.determine_winner("even", "even", 8)
    assert result == "DRAW"

def test_determine_winner_different_choices(referee):
    result = referee.determine_winner("even", "odd", 8)
    assert result == "PLAYER_A"
```

---

### 5.2 Integration Test Approach

**Decision:** Docker Compose for full stack testing

**docker-compose.test.yml:**
```yaml
version: '3.8'
services:
  league_manager:
    build: .
    command: python league_manager.py
    ports:
      - "8000:8000"
  
  referee:
    build: .
    command: python referee.py
    ports:
      - "8001:8001"
  
  player_1:
    build: .
    command: python player_agent.py --port 8101 --strategy random
    ports:
      - "8101:8101"
  
  player_2:
    build: .
    command: python player_agent.py --port 8102 --strategy always_even
    ports:
      - "8102:8102"
```

**Run:**
```bash
docker-compose -f docker-compose.test.yml up
python tests/integration_test.py
```

---

### 5.3 Protocol Compliance Test Suite

**Decision:** Dedicated schema validation tests

**tests/test_protocol_compliance.py:**
```python
def test_game_join_ack_schema():
    valid = {
        "message_type": "GAME_JOIN_ACK",
        "match_id": "R1M1",
        "player_id": "P01",
        "arrival_timestamp": "2025-01-15T10:30:00Z",
        "accept": True
    }
    assert validate_schema(valid, GameJoinAckSchema) == True

def test_parity_choice_only_lowercase():
    invalid = ["EVEN", "Even", "ODD", "Odd", "0", "1"]
    for choice in invalid:
        with pytest.raises(ValidationError):
            ParityChoiceSchema(parity_choice=choice)
```

---

## 6. Deployment Decisions

### 6.1 Local Development Setup

**Decision:** Virtual environment + requirements.txt

**Setup Script:**
```bash
#!/bin/bash
# setup_local.sh

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create necessary directories
mkdir -p data logs

# Generate default config
python scripts/generate_config.py --mode local --players 4

echo "Setup complete! Run: python orchestrator.py"
```

---

### 6.2 Class League Deployment

**✅ FINAL DECISION:** Kubernetes on Cloud (if can be implemented easily), otherwise suggest alternatives

**Primary Option - Kubernetes (GCP, AWS):**
- Auto-scaling for multiple matches
- Resource isolation per player
- Easy monitoring and logs
- Fault tolerance

**Resource Limits per Player:**
```yaml
resources:
  limits:
    cpu: "500m"      # 0.5 CPU cores
    memory: "256Mi"  # 256 MB RAM
  requests:
    cpu: "100m"
    memory: "128Mi"
```

**Alternative Options** (if Kubernetes adds too much complexity):

**Option B: Docker Swarm**
- Simpler than Kubernetes
- Built into Docker
- Good orchestration capabilities
- Easier learning curve

**Option C: Simple VM Deployment**
- Deploy League Manager + Referees on dedicated VMs
- Players deployed across multiple VMs
- Manual load balancing
- Simpler but less scalable

**Recommendation:**
- For 4-10 players: Simple VM deployment sufficient
- For 10-50 players: Consider Docker Swarm
- For production/50+ players: Kubernetes if team has expertise

---

## 7. Section Removed

**Note:** The original Section 7 "Open Questions for User" regarding grading and class league specifics has been removed as it is not relevant for current implementation. Grading is not being done at this time.

---

## Summary of Critical Decisions (Updated)

| # | Decision Area | Chosen Approach | Rationale |
|---|--------------|----------------|-----------|
| 1 | Orchestrator | **Integrated into League Manager & Referee** | Simplifies deployment, natural responsibility |
| 2 | MCP Handshake | **Players register themselves (Option B)** | Autonomous agents, configurable timeout |
| 3 | Registration Timeout | **60 seconds (configurable)** | Flexible for different scenarios |
| 4 | Authentication | **No authentication** | Simplifies implementation | 5 | Random Draws | SystemRandom, no seed | Fairness and unpredictability |
| 6 | Persistence | JSON files for League Manager | Simplicity for homework scale |
| 7 | Concurrency | **Parallel execution, multiple referees** | Performance: 2 referees for 4 players, up to 50 |
| 8 | Same Choice Rule | **Always draw if both choose same** | Confirmed interpretation |
| 9 | Response Timeouts | **5s join, 30s choice, 10s other** | Specific timing requirements |
| 10 | Retry Logic | **3 attempts for invalid, 1 for timeout** | Separate hard/soft failures |
| 11 | Tie-Breaking | **Points, Wins, Draws** | Clear ranking order |
| 12 | Message Structure | **All base fields required in every message** | Self-contained, traceable |
| 13 | Validation | Pydantic schemas | Type safety and auto-validation |
| 14 | Async I/O | httpx with asyncio | Scalability to 50+ players |
| 15 | Game Rules | Protocol-based pluggable module | Extensibility to other games |
| 16 | LLM Integration | Optional with fallback | Demonstrates AI without blocking |
| 17 | Storage | JSON files | No DB setup required |
| 18 | Testing | pytest + Docker Compose | Comprehensive coverage |
| 19 | Deployment | Docker for multi-machine, venv for local | Isolation and portability |


---

**Document Status:** Ready for Implementation  
**Last Updated:** December 2025 (incorporating user feedback)  
**Owner:** Development Team

