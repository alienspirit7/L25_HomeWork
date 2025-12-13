"""League Manager - Orchestrates league operations."""
import asyncio
import argparse
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))

from utils.mcp_server import MCPServer
from utils.mcp_client import MCPClient
from utils.helpers import generate_round_robin_schedule, calculate_standings, get_iso_timestamp
from utils.schemas import PlayerMeta, RegistrationResponse
import uvicorn


class LeagueManager:
    """League Manager MCP Server."""
    
    def __init__(self, config: dict):
        self.config = config
        self.league_id = config['league']['league_id']
        self.registration_timeout = config['league'].get('registration_timeout', 60)
        self.players = {}
        self.player_counter = 0
        self.schedule = []
        self.results = {}
        self.registration_closed = False
        self.completed_matches = set()
        self.expected_matches = 0
        self.mcp_server = MCPServer("LeagueManager")
        self.mcp_client = MCPClient()
        self.referee_endpoints = [
            f"http://{r['host']}:{r['port']}/mcp" 
            for r in config['agents']['referees']
        ]
        self.referee_index = 0
        self._setup_tools()
        logging.info(f"League Manager initialized: {self.league_id}")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("register_player", self.register_player)
        self.mcp_server.register_tool("report_match_result", self.report_match_result)
        self.mcp_server.register_tool("get_standings", self.get_standings)
    
    async def register_player(self, args: dict) -> dict:
        """Handle player registration."""
        if self.registration_closed:
            return {"status": "REJECTED", "reason": "Registration closed"}
        
        player_meta = PlayerMeta(**args.get('player_meta', args))
        
        if self.config['league']['game_type'] not in player_meta.game_types:
            return {"status": "REJECTED", "reason": "Game type not supported"}
        
        self.player_counter += 1
        player_id = f"P{self.player_counter:02d}"
        
        self.players[player_id] = {
            "player_id": player_id,
            "display_name": player_meta.display_name,
            "endpoint": player_meta.contact_endpoint,
            "registered_at": get_iso_timestamp()
        }
        
        logging.info(f"Player registered: {player_id} - {player_meta.display_name}")
        return {"status": "ACCEPTED", "player_id": player_id}
    
    async def report_match_result(self, args: dict) -> dict:
        """Receive match result from referee."""
        match_id = args['match_id']
        self.results[match_id] = {
            "winner": args.get('winner'),
            "score": args['score'],
            "details": args.get('details', {})
        }
        self.completed_matches.add(match_id)
        logging.info(f"Match result recorded: {match_id} ({len(self.completed_matches)}/{self.expected_matches})")
        self._save_state()
        return {"status": "OK"}
    
    async def get_standings(self, args: dict) -> dict:
        """Calculate and return standings."""
        standings = calculate_standings(self.results)
        return {"standings": standings}
    
    def _save_state(self):
        """Persist league state to disk."""
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
        logging.info("Waiting for player registration...")
        await asyncio.sleep(self.registration_timeout)
        self.registration_closed = True
        
        player_ids = list(self.players.keys())
        logging.info(f"Registration closed. Players: {player_ids}")
        
        self.schedule = generate_round_robin_schedule(player_ids)
        self.expected_matches = len(self.schedule)
        logging.info(f"Schedule created: {self.expected_matches} matches")
        
        for player_A, player_B, round_id, match_num in self.schedule:
            match_id = f"R{round_id}M{match_num}"
            referee_endpoint = self.referee_endpoints[self.referee_index]
            self.referee_index = (self.referee_index + 1) % len(self.referee_endpoints)
            
            await self.mcp_client.call_tool(referee_endpoint, "start_match", {
                "match_id": match_id,
                "round_id": round_id,
                "player_A_id": player_A,
                "player_B_id": player_B,
                "player_A_endpoint": self.players[player_A]['endpoint'],
                "player_B_endpoint": self.players[player_B]['endpoint'],
                "league_id": self.league_id,
                "league_manager_endpoint": f"http://{self.config['agents']['league_manager']['host']}:{self.config['agents']['league_manager']['port']}/mcp"
            })
        
        # Wait for all matches to complete
        logging.info("Waiting for all matches to complete...")
        while len(self.completed_matches) < self.expected_matches:
            await asyncio.sleep(1)
        
        logging.info("All matches completed!")
        
        # Calculate final standings
        standings = calculate_standings(self.results)
        
        # Display comprehensive results
        print("\n" + "="*60)
        print("  LEAGUE COMPLETE - FINAL RESULTS")
        print("="*60)
        print(f"\nLeague: {self.league_id}")
        print(f"Total Matches Played: {self.expected_matches}")
        print(f"Total Players: {len(player_ids)}\n")
        
        print("-"*60)
        print("FINAL STANDINGS")
        print("-"*60)
        print(f"{'Rank':<6} {'Player':<12} {'Played':<8} {'W':<4} {'D':<4} {'L':<4} {'Points':<8}")
        print("-"*60)
        
        for entry in standings:
            print(f"{entry['rank']:<6} {entry['player_id']:<12} "
                  f"{entry['played']:<8} {entry['wins']:<4} {entry['draws']:<4} "
                  f"{entry['losses']:<4} {entry['points']:<8}")
        
        # Announce the winner
        if standings:
            winner = standings[0]
            print("\n" + "="*60)
            print("  🏆 WINNER ANNOUNCEMENT 🏆")
            print("="*60)
            print(f"\nCongratulations to {winner['player_id']} - {self.players.get(winner['player_id'], {}).get('display_name', 'Unknown')}!")
            print(f"Final Score: {winner['points']} points ({winner['wins']} wins, {winner['draws']} draws, {winner['losses']} losses)")
            print("\n" + "="*60 + "\n")
        
        logging.info(f"Winner: {winner['player_id']} with {winner['points']} points")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/local_config.yaml")
    args = parser.parse_args()
    
    with open(args.config) as f:
        config = yaml.safe_load(f)
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    manager = LeagueManager(config)
    
    # Create a config for uvicorn
    uvicorn_config = uvicorn.Config(
        manager.mcp_server.app,
        host=config['agents']['league_manager']['host'],
        port=config['agents']['league_manager']['port'],
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
