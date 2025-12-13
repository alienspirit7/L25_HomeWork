# Even/Odd League - Documentation Summary

## Quick Reference Guide

### Documents Created

1. **PDR_EvenOdd_League.md** - Complete Product Design Review
2. **Development_Decisions_and_Missing_Info.md** - Decisions tracking and gap analysis
3. **This file** - Quick reference summary

---

## Project Overview

**Name:** Even/Odd AI Agent League  
**Protocol:** MCP (Model Context Protocol) v2024-11-05  
**Transport:** HTTP + JSON-RPC 2.0  
**LLM:** Gemini API (optional for player strategy)  
**Architecture:** 3-layer (League, Referee, Game Rules)

---

## System Components

### 1. League Manager (Port 8000)
**Role:** MCP Server + Client (League-Level Orchestrator)  
**Orchestrates League-Wide Operations:**
- Player registration and tracking (self-registration with 60s timeout)
- Round-Robin schedule generation
- Standings calculation and ranking
- League-wide announcements

**Tools:**
- `register_player` - Register new players
- `create_schedule` - Generate Round-Robin matches
- `report_match_result` - Receive from referee
- `get_standings` - Return current rankings

### 2. Referee (Port 8001)
**Role:** MCP Server + Client (Match-Level Orchestrator)  
**Orchestrates Match Execution:**
- Match initialization and player invitations
- Choice collection and validation
- Winner determination and result reporting

**Tools:**
- `start_match` - Initialize game
- `collect_choices` - Get player choices
- `draw_number` - Random 1-10
- `finalize_match` - Report to league

### 3. Player Agent (Ports 8101-8104)
**Role:** MCP Server  
**Tools (Required):**
- `handle_game_invitation` - Respond within 5s
- `choose_parity` - Return "even" or "odd" within 30s
- `notify_match_result` - Update internal state

**Registration:**
- Players self-register by calling League Manager's `register_player` tool
- Registration window: configurable (default 60 seconds)
- Late registrations are rejected



---

## Critical Input/Output Schemas

### Player Registration
```json
Input: {
  "display_name": "Agent Alpha",
  "version": "1.0.0",
  "game_types": ["even_odd"],
  "contact_endpoint": "http://localhost:8101/mcp"
}

Output: {
  "status": "ACCEPTED|REJECTED",
  "player_id": "P01",
  "reason": null
}
```

### Game Invitation
```json
Input: {
  "message_type": "GAME_INVITATION",
  "match_id": "R1M1",
  "game_type": "even_odd",
  "opponent_id": "P02",
  "role_in_match": "PLAYER_A|PLAYER_B"
}

Output (< 5 seconds): {
  "message_type": "GAME_JOIN_ACK",
  "match_id": "R1M1",
  "player_id": "P01",
  "arrival_timestamp": "2025-01-15T10:30:00Z",
  "accept": true
}
```

### Choose Parity
```json
Input: {
  "message_type": "CHOOSE_PARITY_CALL",
  "match_id": "R1M1",
  "player_id": "P01",
  "game_type": "even_odd",
  "context": {
    "opponent_id": "P02",
    "your_standings": {"wins": 2, "losses": 1, "draws": 0}
  }
}

Output (< 30 seconds): {
  "message_type": "CHOOSE_PARITY_RESPONSE",
  "match_id": "R1M1",
  "player_id": "P01",
  "parity_choice": "even"  // MUST be exactly "even" or "odd"
}
```

### Game Over
```json
Input: {
  "message_type": "GAME_OVER",
  "match_id": "R1M1",
  "game_result": {
    "status": "WIN|DRAW|TECHNICAL_LOSS",
    "winner_player_id": "P01",
    "drawn_number": 8,
    "number_parity": "even",
    "choices": {"P01": "even", "P02": "odd"},
    "reason": "P01 chose even, number was 8 (even)"
  }
}
```

---

## Game Rules (Even/Odd)

### Win Condition
1. Draw random number 1-10
2. Determine parity: "even" if number % 2 == 0, else "odd"
3. Winner logic:
   ```python
   if choice_A == choice_B:
       return "DRAW"  # Always draw if same choice
   elif choice_A == parity:
       return "PLAYER_A"
   else:
       return "PLAYER_B"
   ```

### Scoring
- Win: 3 points
- Draw: 1 point each
- Loss: 0 points

### Tie-Breaking
1. Total points (descending)
2. Wins (descending)
3. Ties (descending) - Note: Ties/Draws are synonymous
4. Head-to-head (if applicable)
5. Alphabetical by player_id

---

## Testing Workflows

### Local Testing (Single Machine)

**Terminal 1:**
```bash
python league_manager.py --port 8000
```

**Terminal 2:**
```bash
python referee.py --port 8001
```

**Terminal 3-6:**
```bash
python player_agent.py --port 8101 --strategy random
python player_agent.py --port 8102 --strategy random
python player_agent.py --port 8103 --strategy always_even
python player_agent.py --port 8104 --strategy always_odd
```

**Terminal 7:**
```bash
python orchestrator.py --config config.json
```

### Multi-Machine Testing

**Machine A (192.168.1.10):**
- League Manager :8000
- Referee :8001

**Machine B (192.168.1.11):**
- Player 1 :8101
- Player 2 :8102

**Update config.json:**
```json
{
  "league_manager": "http://192.168.1.10:8000/mcp",
  "referee": "http://192.168.1.10:8001/mcp",
  "players": [
    {"id": "P01", "endpoint": "http://192.168.1.11:8101/mcp"},
    {"id": "P02", "endpoint": "http://192.168.1.11:8102/mcp"}
  ]
}
```

---

## Key Validation Rules

### CRITICAL - Protocol Compliance

1. **Parity Choice:** MUST be exactly "even" or "odd" (lowercase)
   - ❌ Invalid: "EVEN", "Even", "ODD", "0", "1"
   - ✅ Valid: "even", "odd"

2. **Timestamps:** ISO-8601 with Z suffix
   - ✅ Valid: "2025-01-15T10:30:00Z"
   - ❌ Invalid: "2025-01-15 10:30:00"

3. **Response Times:**
   - GAME_JOIN_ACK: < 5 seconds
   - CHOOSE_PARITY_RESPONSE: < 30 seconds
   - Failure = Technical Loss

4. **Message Structure:**
   - All messages wrapped in JSON-RPC 2.0
   - Required field: `jsonrpc: "2.0"`
   - Requests have `id`, notifications don't

---

## State Machines

### Match Execution States
```
WAITING_FOR_PLAYERS 
  → (both joined) → COLLECTING_CHOICES
  → (timeout) → TECHNICAL_LOSS

COLLECTING_CHOICES
  → (both responded) → DRAWING_NUMBER
  → (timeout) → TECHNICAL_LOSS
  → (invalid 3x) → TECHNICAL_LOSS

DRAWING_NUMBER
  → (auto) → FINISHED

FINISHED
  → (reported) → IDLE
```

### Player States
```
IDLE 
  → GAME_INVITATION → INVITED
  → GAME_JOIN_ACK sent → PLAYING
  → CHOOSE_PARITY_RESPONSE sent → AWAITING_RESULT
  → GAME_OVER received → IDLE
```

---

## Error Handling

### Timeout Scenarios
| Event | Timeout | Action |
|-------|---------|--------|
| GAME_JOIN_ACK not received | 5s | Technical loss |
| CHOOSE_PARITY_RESPONSE not received | 30s | Technical loss |
| HTTP request (general) | 10s | Retry once |

### Invalid Move Handling
1. Receive invalid `parity_choice` (e.g., "EVEN")
2. Send `MOVE_REJECTED` message
3. Retry (max 3 attempts)
4. After 3 failures → Technical Loss

### Network Failures
- **Player disconnect:** Mark as technical loss, continue league
- **Referee crash:** Abort match, reschedule at end
- **League Manager crash:** Load from `league_state.json`, resume

---

## Deployment Scenarios

### Scenario 1: Local Development
- All components on localhost
- Different ports (8000, 8001, 8101-8104)
- No authentication needed

### Scenario 2: Local Network
- League Manager + Referee on one machine
- Players distributed across machines
- Use IP addresses in config
- Open firewall ports

### Scenario 3: Cloud (Class League)
- Kubernetes deployment
- TLS encryption (HTTPS)
- Token authentication
- Resource limits per player

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Match duration | < 60s | End-to-end |
| API response | < 100ms (p95) | Per-call |
| Concurrent matches | 10+ | Load test |
| League size | Up to 100 players | Stress test |

**Scaling:**
- 4 players: 6 matches × 1 min = 6 minutes (sequential)
- 100 players: 4,950 matches → Use parallel execution

---

## File Structure

```
even_odd_league/
├── orchestrator.py           # MCP Client, coordinates all
├── league_manager.py         # MCP Server :8000
├── referee.py                # MCP Server :8001
├── player_agent.py           # MCP Server :8101-8104
├── game_rules/
│   └── even_odd.py          # Pluggable game logic
├── config.json              # Endpoints configuration
├── requirements.txt         # Python dependencies
├── tests/
│   ├── test_protocol.py     # Schema validation
│   ├── test_integration.py  # Full league test
│   └── dummy_agents/        # Test players
├── data/
│   ├── league_state.json    # Persistent state
│   └── match_history.json   # Audit trail
└── logs/
    ├── league_manager.log
    ├── referee.log
    └── player_*.log
```

---

## Dependencies (requirements.txt)

```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.1
pydantic==2.5.0
python-multipart==0.0.6
google-generativeai==0.3.1  # For LLM strategy (optional)
pytest==7.4.3               # Testing
pyyaml==6.0.1               # Config parsing
```

---

## Quick Start Commands

### 1. Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate Config
```bash
python scripts/generate_config.py --mode local --players 4
```

### 3. Run League
```bash
# Start all components (requires tmux or multiple terminals)
./scripts/start_local_league.sh
```

### 4. Run Tests
```bash
pytest tests/ -v
```

---

## MCP Protocol Cheat Sheet

### Initialization Sequence
```
Client → Server: initialize
Server → Client: initializeResult  
Client → Server: initialized (notification)
```

### Tool Discovery
```
Client → Server: tools/list
Server → Client: [list of available tools]
```

### Tool Call
```
Client → Server: tools/call {name: "choose_parity", arguments: {...}}
Server → Client: result: {content: [...]}
```

### JSON-RPC Request
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {"name": "tool_name", "arguments": {...}},
  "id": 1
}
```

### JSON-RPC Response (Success)
```json
{
  "jsonrpc": "2.0",
  "result": {...},
  "id": 1
}
```

### JSON-RPC Response (Error)
```json
{
  "jsonrpc": "2.0",
  "error": {"code": -32601, "message": "Method not found"},
  "id": 1
}
```

---

## Decision Quick Reference

| Question | Decision | Rationale |
|----------|----------|-----------|
| Orchestrator architecture? | **Integrated into League Manager & Referee** | Simplifies deployment, natural responsibility |
| Who initiates registration? | **Players self-register** | Autonomous agents initiate own registration |
| Registration timeout? | **60s (configurable)** | Flexible for different deployment scenarios |
| Both choose same → result? | Always DRAW | Simpler logic, fair game |
| Retry invalid moves? | Yes, max 3 | Balance fairness/speed |
| Persistence format? | JSON files | Simple, human-readable |
| Async or sync? | Async (httpx) | Scalability |
| LLM required? | No, optional | Demonstrates but not blocking |
| Authentication? | **No authentication** | Simplifies implementation for educational use |
| Random seed? | No (SystemRandom) | True randomness |
| Multiple referees? | **Yes, parallel execution** | 2 referees for 4 players, scales to 50 |
| Database? | No (JSON) | Homework scale sufficient |

---

## Common Pitfalls to Avoid

1. **❌ Using uppercase "EVEN" instead of "even"**
   - Always lowercase: `"even"` or `"odd"`

2. **❌ Missing ISO-8601 Z suffix in timestamps**
   - Correct: `"2025-01-15T10:30:00Z"`

3. **❌ Not implementing all required tools**
   - Player needs: `handle_game_invitation`, `choose_parity`, `notify_match_result`

4. **❌ Exceeding timeout limits**
   - 5s for GAME_JOIN_ACK
   - 30s for CHOOSE_PARITY_RESPONSE

5. **❌ Not handling same-choice logic correctly**
   - If both choose "even" → DRAW (regardless of number)

6. **❌ Forgetting MCP initialization handshake**
   - Must complete: initialize → initializeResult → initialized

7. **❌ Using sync HTTP in production**
   - Use `httpx` with async for scalability

8. **❌ Not persisting league state**
   - Save after each match to prevent data loss

9. **❌ Hardcoding endpoints instead of config file**
   - Use config.json for flexibility

10. **❌ No error logging**
    - Always log errors for debugging

---

## Troubleshooting

### Problem: Player not responding
**Check:**
1. Is player process running? `curl http://localhost:8101/mcp`
2. Firewall blocking? `telnet localhost 8101`
3. Check player logs for errors

### Problem: "Method not found" error
**Cause:** Tool name mismatch
**Fix:** Verify tool name in `tools/list` matches `tools/call`

### Problem: "Invalid params" error
**Cause:** Schema mismatch
**Fix:** Validate JSON against inputSchema

### Problem: League Manager crashes
**Recovery:**
1. Check `league_state.json` exists
2. Restart League Manager
3. It will resume from last saved state

---

## Next Steps for Implementation

1. ✅ Read and understand PDR document
2. ✅ Review decisions document
3. ⬜ Implement basic MCP server (League Manager)
4. ⬜ Implement Referee with Even/Odd rules
5. ⬜ Implement simple Player Agent (random strategy)
6. ⬜ Test locally with 4 players
7. ⬜ Add LLM strategy (optional)
8. ⬜ Test on multiple machines
9. ⬜ Submit to class league

---

## References

- **Full PDR:** `PDR_EvenOdd_League.md`
- **Decisions Log:** `Development_Decisions_and_Missing_Info.md`
- **MCP Spec:** https://modelcontextprotocol.io/
- **JSON-RPC 2.0:** https://www.jsonrpc.org/specification
- **Gemini API:** https://ai.google.dev/tutorials/python_quickstart

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Status:** Ready for Development
