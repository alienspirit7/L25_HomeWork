"""
League Manager - Entry point and main orchestration.

This demonstrates the modular architecture pattern from Section 11.
The monolithic src/league_manager.py has been split into:
  - main.py: Entry point, initialization, server startup
  - handlers.py: Message handling logic
  - scheduler.py: Round management and scheduling

Usage:
  python main.py --league-id league_2025_even_odd
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
import sys
import uvicorn

# Add parent directories to path for imports during transition
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from league_sdk (new structure)
from league_sdk import ConfigLoader, JsonLogger
from league_sdk.mcp_server import MCPServer
from league_sdk.mcp_client import MCPClient

# Import modular components
from handlers import LeagueHandlers
from scheduler import LeagueScheduler


class LeagueManager:
    """
    League Manager - Orchestrates league operations.
    
    Now using modular architecture with SDK integration.
    """
    
    def __init__(self, league_id: str):
        """Initialize League Manager using SDK configuration."""
        # Load configuration using SDK
        config_loader = ConfigLoader()
        self.system_config = config_loader.load_system()
        self.league_config = config_loader.load_league(league_id)
        self.agents_config = config_loader.load_agents()
        
        self.league_id = league_id
        self.registration_timeout = self.league_config.settings.registration_timeout_sec
        
        # Initialize SDK logger
        self.logger = JsonLogger("league_manager", league_id=league_id)
        self.logger.info("MANAGER_INITIALIZED", league_id=league_id)
        
        # Player and referee registries
        self.players = {}
        self.player_counter = 0
        self.player_tokens = {}
        
        self.referees = {}
        self.referee_counter = 0
        self.referee_tokens = {}
        
        # League state
        self.schedule = []
        self.results = {}
        self.registration_closed = False
        self.completed_matches = set()
        self.expected_matches = 0
        
        # Round tracking
        self.rounds_info = {}
        self.completed_rounds = set()
        self.total_rounds = 0
        
        # MCP components
        self.mcp_server = MCPServer("LeagueManager")
        self.mcp_client = MCPClient()
        
        # Initialize modular components
        self.handlers = LeagueHandlers(self)
        self.scheduler = LeagueScheduler(self)
        
        # Get referee endpoints from config
        self.referee_endpoints = [
            ref.endpoint for ref in self.agents_config.referees if ref.active
        ]
        self.referee_index = 0
        
        self._setup_tools()
        logging.info(f"League Manager initialized: {self.league_id}")
    
    def _setup_tools(self):
        """Register MCP tools using modular handlers."""
        self.mcp_server.register_tool("register_referee", self.handlers.register_referee)
        self.mcp_server.register_tool("register_player", self.handlers.register_player)
        self.mcp_server.register_tool("report_match_result", self.handlers.report_match_result)
        self.mcp_server.register_tool("get_standings", self.handlers.get_standings)
        self.mcp_server.register_tool("handle_league_query", self.handlers.handle_league_query)
    
    def _validate_auth_token(self, sender: str, provided_token: str) -> bool:
        """Validate authentication token for sender."""
        if not provided_token or ":" not in sender:
            return False
        
        agent_type, agent_id = sender.split(":", 1)
        
        if agent_type == "player":
            return self.player_tokens.get(agent_id) == provided_token
        elif agent_type == "referee":
            return self.referee_tokens.get(agent_id) == provided_token
        
        return False
    
    def _save_state(self):
        """Persist league state (temporary - should use repositories)."""
        Path("data").mkdir(exist_ok=True)
        with open("data/league_state.json", "w") as f:
            json.dump({
                "league_id": self.league_id,
                "players": self.players,
                "results": self.results,
                "schedule": self.schedule
            }, f, indent=2)
    
    async def run_league(self):
        """Execute full league workflow."""
        self.logger.info("REGISTRATION_STARTED", timeout_sec=self.registration_timeout)
        
        await asyncio.sleep(self.registration_timeout)
        self.registration_closed = True
        
        player_ids = list(self.players.keys())
        self.logger.info("REGISTRATION_CLOSED", player_count=len(player_ids))
        
        # Generate schedule using scheduler
        self.scheduler.generate_schedule(player_ids)
        
        # Group matches by round
        rounds_matches = self._group_matches_by_round()
        
        # Execute rounds with announcements        
        for round_id in sorted(rounds_matches.keys()):
            round_matches = rounds_matches[round_id]
            
            # Send ROUND_ANNOUNCEMENT
            await self.scheduler.announce_round(round_id, round_matches)
            
            # Start all matches in round
            await self._start_round_matches(round_matches)
        
        # Wait for completion
        await self._wait_for_completion()
        
        # Send final results
        await self._finalize_league()
    
    def _group_matches_by_round(self):
        """Group schedule matches by round."""
        rounds_matches = {}
        for player_A, player_B, round_id, match_num in self.schedule:
            if round_id not in rounds_matches:
                rounds_matches[round_id] = []
            
            match_id = f"R{round_id}M{match_num}"
            referee_endpoint = self.referee_endpoints[self.referee_index]
            self.referee_index = (self.referee_index + 1) % len(self.referee_endpoints)
            
            rounds_matches[round_id].append({
                "match_id": match_id,
                "player_A_id": player_A,
                "player_B_id": player_B,
                "player_A_endpoint": self.players[player_A]['endpoint'],
                "player_B_endpoint": self.players[player_B]['endpoint'],
                "referee_endpoint": referee_endpoint,
                "round_id": round_id
            })
        
        return rounds_matches
    
    async def _start_round_matches(self, round_matches):
        """Start all matches in a round."""
        for match_info in round_matches:
            await self.mcp_client.call_tool(
                match_info['referee_endpoint'],
                "start_match",
                {
                    "match_id": match_info['match_id'],
                    "round_id": match_info['round_id'],
                    "player_A_id": match_info['player_A_id'],
                    "player_B_id": match_info['player_B_id'],
                    "player_A_endpoint": match_info['player_A_endpoint'],
                    "player_B_endpoint": match_info['player_B_endpoint'],
                    "league_id": self.league_id,
                    "league_manager_endpoint": f"http://{self.system_config.network.base_host}:{self.system_config.network.default_league_manager_port}/mcp"
                }
            )
    
    async def _wait_for_completion(self):
        """Wait for all matches to complete."""
        while len(self.completed_matches) < self.expected_matches:
            await asyncio.sleep(1)
        self.logger.info("ALL_MATCHES_COMPLETED", total=self.expected_matches)
    
    async def _finalize_league(self):
        """Calculate final standings and send completion message."""
        from league_sdk.helpers import calculate_standings
        
        standings = calculate_standings(self.results)
        await self.scheduler.send_league_completed(standings)
        
        # Display results
        self._display_final_results(standings)
    
    def _display_final_results(self, standings):
        """Print comprehensive final results."""
        print("\n" + "="*60)
        print("  LEAGUE COMPLETE - FINAL RESULTS")
        print("="*60)
        print(f"\nLeague: {self.league_id}")
        print(f"Total Matches: {self.expected_matches}\n")
        
        print("-"*60)
        print(f"{'Rank':<6} {'Player':<12} {'Played':<8} {'W':<4} {'D':<4} {'L':<4} {'Points':<8}")
        print("-"*60)
        
        for entry in standings:
            print(f"{entry['rank']:<6} {entry['player_id']:<12} "
                  f"{entry['played']:<8} {entry['wins']:<4} {entry['draws']:<4} "
                  f"{entry['losses']:<4} {entry['points']:<8}")
        
        if standings:
            winner = standings[0]
            print("\n" + "="*60)
            print("  🏆 WINNER 🏆")
            print("="*60)
            print(f"\n{winner['player_id']} - {winner['points']} points")
            print("="*60 + "\n")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="League Manager - Protocol V2")
    parser.add_argument("--league-id", default="league_2025_even_odd", help="League identifier")
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize manager
    manager = LeagueManager(args.league_id)
    
    # Get network config from SDK
    config_loader = ConfigLoader()
    system_config = config_loader.load_system()
    
    # Create uvicorn server
    uvicorn_config = uvicorn.Config(
        manager.mcp_server.app,
        host=system_config.network.base_host,
        port=system_config.network.default_league_manager_port,
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    
    # Run both server and league manager concurrently
    await asyncio.gather(
        server.serve(),
        manager.run_league()
    )


if __name__ == "__main__":
    asyncio.run(main())
