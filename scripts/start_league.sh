#!/bin/bash
# Start League Manager, 2 Referees, and 4 Players for local testing

echo "=== Starting Even/Odd League System ==="
echo ""

# Create directories if they don't exist
mkdir -p data logs

# Start League Manager
echo "Starting League Manager on port 8000..."
python src/league_manager.py --config config/local_config.yaml > logs/league_manager.log 2>&1 &
LEAGUE_PID=$!
sleep 2

# Start 2 Referee instances for parallel match execution
echo "Starting Referee #1 on port 8001..."
python src/referee.py --port 8001 > logs/referee_8001.log 2>&1 &
REF1_PID=$!

echo "Starting Referee #2 on port 8002..."
python src/referee.py --port 8002 > logs/referee_8002.log 2>&1 &
REF2_PID=$!
sleep 2

# Start 4 Player Agents with different strategies
echo "Starting Player Agents..."
python src/player_agent.py --port 8101 --strategy random --name "Alpha" --league "http://localhost:8000/mcp" > logs/player_8101.log 2>&1 &
P1_PID=$!

python src/player_agent.py --port 8102 --strategy always_even --name "Beta" --league "http://localhost:8000/mcp" > logs/player_8102.log 2>&1 &
P2_PID=$!

python src/player_agent.py --port 8103 --strategy always_odd --name "Gamma" --league "http://localhost:8000/mcp" > logs/player_8103.log 2>&1 &
P3_PID=$!

python src/player_agent.py --port 8104 --strategy random --name "Delta" --league "http://localhost:8000/mcp" > logs/player_8104.log 2>&1 &
P4_PID=$!

echo ""
echo "✓ All agents started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "League Manager:  http://localhost:8000"
echo "Referees:        http://localhost:8001, http://localhost:8002"
echo "Players:         http://localhost:8101-8104"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Logs available in logs/ directory"
echo "Press Ctrl+C to stop all processes"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping all agents..."
    kill $LEAGUE_PID $REF1_PID $REF2_PID $P1_PID $P2_PID $P3_PID $P4_PID 2>/dev/null
    echo "All processes stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait indefinitely
wait
