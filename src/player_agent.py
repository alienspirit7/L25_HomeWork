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
    
    async def handle_game_invitation(self, args: dict) -> dict:
        """Respond to game invitation."""
        match_id = args.get('match_id')
        logging.info(f"Received invitation for match {match_id}")
        
        response = {
            "protocol": "league.v1",
            "message_type": "GAME_JOIN_ACK",
            "league_id": args.get('league_id', ''),
            "round_id": args.get('round_id', 0),
            "match_id": match_id,
            "conversation_id": args.get('conversation_id', ''),
            "sender": f"player:{self.player_id}",
            "timestamp": get_iso_timestamp(),
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
            "protocol": "league.v1",
            "message_type": "CHOOSE_PARITY_RESPONSE",
            "league_id": args.get('league_id', ''),
            "round_id": args.get('round_id', 0),
            "match_id": match_id,
            "conversation_id": args.get('conversation_id', ''),
            "sender": f"player:{self.player_id}",
            "timestamp": get_iso_timestamp(),
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
    
    async def register_with_league(self, league_manager_url: str):
        """Register with League Manager."""
        player_meta = {
            "display_name": self.display_name,
            "version": "1.0.0",
            "game_types": ["even_odd"],
            "contact_endpoint": f"http://localhost:{self.port}/mcp"
        }
        
        result = await self.mcp_client.call_tool(
            league_manager_url,
            "register_player",
            {"player_meta": player_meta}
        )
        
        result_text = result.get('content', [{}])[0].get('text', '{}')
        result_data = json.loads(result_text)
        
        if result_data.get('status') == 'ACCEPTED':
            self.player_id = result_data['player_id']
            logging.info(f"Registration successful: {self.player_id}")
        else:
            logging.error(f"Registration failed: {result_data.get('reason')}")


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
