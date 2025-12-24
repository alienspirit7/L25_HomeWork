#!/bin/bash
# Quick test script to start all agents in sequence

echo "Starting League Manager..."
cd agents/league_manager
python main.py --league-id league_2025_even_odd &
LEAGUE_PID=$!

echo "Waiting for league manager to be ready..."
sleep 5

echo "Starting Referees..."
cd ../referee_REF01
python main.py --referee-id REF01 --port 8001 --league-manager http://localhost:8000/mcp &
cd ../referee_REF02
python main.py --referee-id REF02 --port 8002 --league-manager http://localhost:8000/mcp &

echo "Starting Players..."
cd ../player_P01
python main.py --player-id P01 --port 8101 --strategy random --league-manager http://localhost:8000/mcp &
cd ../player_P02
python main.py --player-id P02 --port 8102 --strategy always_even --league-manager http://localhost:8000/mcp &
cd ../player_P03
python main.py --player-id P03 --port 8103 --strategy always_odd --league-manager http://localhost:8000/mcp &
cd ../player_P04
python main.py --player-id P04 --port 8104 --strategy random --league-manager http://localhost:8000/mcp &

echo "All agents started! Press Ctrl+C to stop all."
wait $LEAGUE_PID
