"""Player Agent - Autonomous game playing agent."""
import asyncio
import argparse
import logging
import random
import os
from pathlib import Path
import sys
import json
sys.path.append(str(Path(__file__).parent))

from utils.mcp_server import MCPServer
from utils.mcp_client import MCPClient
from utils.helpers import get_iso_timestamp, setup_logging
from utils.schemas import PlayerMeta
import uvicorn


class PlayerAgent:
    """Player Agent MCP Server."""
    
    def __init__(self, port: int, strategy: str, display_name: str):
        self.port = port
        self.strategy = strategy
        self.display_name = display_name
        self.player_id = None
        self.auth_token = None  # Received after registration
        self.mcp_server = MCPServer(f"Player-{display_name}")
        self.mcp_client = MCPClient()
        self.match_history = []
        self._setup_tools()
        logging.info(f"Player Agent '{display_name}' initialized with {strategy} strategy")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("handle_game_invitation", self.handle_game_invitation)
        self.mcp_server.register_tool("choose_parity", self.choose_parity)
        self.mcp_server.register_tool("notify_match_result", self.notify_match_result)
        self.mcp_server.register_tool("notify_standings", self.notify_standings)
        self.mcp_server.register_tool("notify_round", self.notify_round)
        self.mcp_server.register_tool("notify_round_completed", self.notify_round_completed)
        self.mcp_server.register_tool("notify_league_completed", self.notify_league_completed)
    
    async def handle_game_invitation(self, args: dict) -> dict:
        """Respond to game invitation."""
        match_id = args.get('match_id')
        logging.info(f"Received invitation for match {match_id}")
        
        response = {
            "protocol": "league.v2",
            "message_type": "GAME_JOIN_ACK",
            "league_id": args.get('league_id', ''),
            "round_id": args.get('round_id', 0),
            "match_id": match_id,
            "conversation_id": args.get('conversation_id', ''),
            "sender": f"player:{self.player_id}",
            "timestamp": get_iso_timestamp(),
            "auth_token": self.auth_token,
            "player_id": self.player_id or "unknown",
            "arrival_timestamp": get_iso_timestamp(),
            "accept": True
        }
        
        return response
    
    async def choose_parity(self, args: dict) -> dict:
        """Choose even or odd based on strategy."""
        match_id = args.get('match_id')
        
        # Apply strategy
        if self.strategy == "random":
            choice = random.choice(["even", "odd"])
        elif self.strategy == "always_even":
            choice = "even"
        elif self.strategy == "always_odd":
            choice = "odd"
        elif self.strategy == "llm":
            choice = await self._llm_choice(args)
        else:
            choice = "even"
        
        logging.info(f"Match {match_id}: Choosing '{choice}'")
        
        response = {
            "protocol": "league.v2",
            "message_type": "CHOOSE_PARITY_RESPONSE",
            "league_id": args.get('league_id', ''),
            "round_id": args.get('round_id', 0),
            "match_id": match_id,
            "conversation_id": args.get('conversation_id', ''),
            "sender": f"player:{self.player_id}",
            "timestamp": get_iso_timestamp(),
            "auth_token": self.auth_token,
            "player_id": self.player_id or "unknown",
            "parity_choice": choice
        }
        
        return response
    
    async def notify_match_result(self, args: dict) -> dict:
        """Receive match result notification."""
        match_id = args.get('match_id')
        game_result = args.get('game_result', {})
        
        self.match_history.append({
            "match_id": match_id,
            "result": game_result,
            "timestamp": get_iso_timestamp()
        })
        
        winner = game_result.get('winner_player_id')
        status = "WON" if winner == self.player_id else ("DREW" if not winner else "LOST")
        logging.info(f"Match {match_id}: {status}")
        
        return {"status": "ACK"}
    
    async def notify_standings(self, args: dict) -> dict:
        """Receive round standings notification from league manager."""
        round_id = args.get('round_id')
        total_rounds = args.get('total_rounds')
        standings = args.get('standings', [])
        
        logging.info(f"\n{'='*60}")
        logging.info(f"STANDINGS AFTER ROUND {round_id}/{total_rounds}")
        logging.info(f"{'='*60}")
        logging.info(f"{'Rank':<6} {'Player':<12} {'Played':<8} {'W':<4} {'D':<4} {'L':<4} {'Points':<8}")
        logging.info(f"{'-'*60}")
        
        for entry in standings:
            logging.info(
                f"{entry['rank']:<6} {entry['player_id']:<12} "
                f"{entry['played']:<8} {entry['wins']:<4} {entry['draws']:<4} "
                f"{entry['losses']:<4} {entry['points']:<8}"
            )
        
        # Highlight own position
        own_standing = next((s for s in standings if s['player_id'] == self.player_id), None)
        if own_standing:
            logging.info(f"\nMy position: #{own_standing['rank']} with {own_standing['points']} points")
        
        logging.info(f"{'='*60}\n")
        
        return {"status": "ACK"}
    
    async def _llm_choice(self, context: dict) -> str:
        """Use Gemini LLM for choice (with fallback)."""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return random.choice(["even", "odd"])
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""You are playing Even/Odd game.
            Context: {context.get('context', {})}
            History: {self.match_history[-3:]}
            
            Choose 'even' or 'odd'. Reply with only that single word (lowercase)."""
            
            response = model.generate_content(prompt)
            choice = response.text.strip().lower()
            
            return choice if choice in ["even", "odd"] else "even"
        except:
            return random.choice(["even", "odd"])
    
    async def notify_round(self, args: dict) -> dict:
        """Receive round announcement from league manager."""
        round_id = args.get('round_id')
        matches = args.get('matches', [])
        
        logging.info(f"[Round {round_id}] Announcement received: {len(matches)} matches scheduled")
        
        # Check if this player is in any matches
        my_matches = [
            m for m in matches
            if m.get ('player_A_id') == self.player_id or m.get('player_B_id') == self.player_id
        ]
        
        if my_matches:
            for match in my_matches:
                opponent = match.get('player_B_id') if match.get('player_A_id') == self.player_id else match.get('player_A_id')
                logging.info(f"  - Match {match.get('match_id')}: vs {opponent}")
        
        return {"status": "ok"}
    
    async def notify_round_completed(self, args: dict) -> dict:
        """Receive round completion notification from league manager."""
        round_id = args.get('round_id')
        next_round_id = args.get('next_round_id')
        summary = args.get('summary', {})
        
        logging.info(f"[Round {round_id}] Completed")
        logging.info(f"  Summary: {summary.get('total_matches')} matches, "
                     f"{summary.get('wins')} decisive, {summary.get('draws')} draws")
        
        if next_round_id:
            logging.info(f"  Next: Round {next_round_id}")
        else:
            logging.info("  Final round completed")
        
        return {"status": "ok"}
    
    async def notify_league_completed(self, args: dict) -> dict:
        """Receive league completion notification."""
        champion = args.get('champion', {})
        final_standings = args.get('final_standings', [])
        total_rounds = args.get('total_rounds')
        total_matches = args.get('total_matches')
        
        logging.info("=" * 60)
        logging.info("LEAGUE COMPLETED")
        logging.info("=" * 60)
        logging.info(f"Champion: {champion.get('player_id')} - {champion.get('display_name')} "
                     f"({champion.get('points')} points)")
        logging.info(f"Total Rounds: {total_rounds}")
        logging.info(f"Total Matches: {total_matches}")
        
        # Find my position
        my_position = next((s for s in final_standings if s['player_id'] == self.player_id), None)
        if my_position:
            logging.info(f"My Final Position: #{my_position['rank']} ({my_position['points']} points)")
        
        logging.info("=" * 60)
        
        return {"status": "ok"}
    
    async def register_with_league(self, league_manager_url: str):
        """Register with League Manager."""
        player_meta = {
            "display_name": self.display_name,
            "version": "1.0.0",
            "protocol_version": "2.1.0",
            "game_types": ["even_odd"],
            "contact_endpoint": f"http://localhost:{self.port}/mcp"
        }
        
        try:
            result = await self.mcp_client.call_tool(
                league_manager_url,
                "register_player",
                {"player_meta": player_meta}
            )
            
            result_text = result.get('content', [{}])[0].get('text', '{}')
            result_data = json.loads(result_text)
            
            if result_data.get('status') == 'ACCEPTED':
                self.player_id = result_data['player_id']
                self.auth_token = result_data.get('auth_token')
                logging.info(f"Registration successful: {self.player_id}")
                if self.auth_token:
                    logging.info(f"Auth token received: {self.auth_token[:20]}...")
            else:
                logging.error(f"Registration failed: {result_data.get('reason')}")
        except Exception as e:
            logging.error(f"Registration error: {e}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--strategy", default="random", choices=["random", "always_even", "always_odd", "llm"])
    parser.add_argument("--name", required=True)
    parser.add_argument("--league", default="http://localhost:8000/mcp")
    args = parser.parse_args()
    
    # Setup logging with file output
    setup_logging(
        log_dir='logs',
        log_file=f'player_{args.name.replace(" ", "_")}_{args.port}.log',
        level='INFO'
    )
    
    player = PlayerAgent(args.port, args.strategy, args.name)
    
    # Create uvicorn config
    uvicorn_config = uvicorn.Config(
        player.mcp_server.app,
        host="localhost",
        port=args.port,
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    
    # Run server and registration concurrently
    await asyncio.gather(
        server.serve(),
        player.register_with_league(args.league)
    )


if __name__ == "__main__":
    asyncio.run(main())
