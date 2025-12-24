"""Player Agent - Template for Protocol V2. Modular architecture."""
import asyncio
import argparse
import logging
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from league_sdk import ConfigLoader, JsonLogger
from league_sdk.mcp_server import MCPServer
from league_sdk.mcp_client import MCPClient
from handlers import PlayerHandlers

class PlayerAgent:
    """Player Agent using modular architecture and SDK."""
    
    def __init__(self, player_id: str, league_id: str, strategy: str, league_manager_url: str, port: int):
        config_loader = ConfigLoader()
        self.system_config = config_loader.load_system()
        self.player_config = config_loader.get_player_by_id(player_id)
        self.player_id = player_id
        self.league_id = league_id
        self.strategy = strategy
        self.league_manager_url = league_manager_url
        self.port = port
        self.auth_token = None
        self.logger = JsonLogger(f"player:{player_id}", league_id=league_id)
        self.logger.info("PLAYER_INIT", player_id=player_id)
        self.mcp_server = MCPServer(f"Player-{player_id}")
        self.mcp_client = MCPClient()
        self.handlers = PlayerHandlers(self)
        self._setup_tools()
        logging.info(f"Player {player_id} initialized with strategy: {self.strategy}")
    
    def _setup_tools(self):
        self.mcp_server.register_tool("notify_round", self.notify_round)
        self.mcp_server.register_tool("notify_standings", self.notify_standings)
        self.mcp_server.register_tool("notify_round_completed", self.notify_round_completed)
        self.mcp_server.register_tool("notify_league_completed", self.notify_league_completed)
        self.mcp_server.register_tool("receive_game_invitation", self.handlers.receive_game_invitation)
        self.mcp_server.register_tool("choose_parity", self.handlers.choose_parity)
        self.mcp_server.register_tool("receive_game_over", self.handlers.receive_game_over)
    
    async def notify_round(self, args: dict) -> dict:
        self.logger.info("ROUND_NOTIFIED", round_id=args.get('round_id'))
        return {"status": "ACK"}
    
    async def notify_standings(self, args: dict) -> dict:
        self.logger.info("STANDINGS_RECEIVED", count=len(args.get('standings', [])))
        return {"status": "ACK"}
    
    async def notify_round_completed(self, args: dict) -> dict:
        self.logger.info("ROUND_COMPLETED", round_id=args.get('round_id'))
        return {"status": "ACK"}
    
    async def notify_league_completed(self, args: dict) -> dict:
        self.logger.info("LEAGUE_COMPLETED", champion=args.get('champion', {}).get('player_id'))
        return {"status": "ACK"}
    
    async def register_with_league(self):
        try:
            import json
            player_meta = {
                "protocol_version": "2.1.0",
                "display_name": f"Player-{self.player_id}",
                "game_types": ["even_odd"],
                "contact_endpoint": f"http://localhost:{self.port}/mcp",
                "strategy": self.strategy
            }
            response = await self.mcp_client.call_tool(
                self.league_manager_url, "register_player", {"player_meta": player_meta}
            )
            if 'content' in response and len(response['content']) > 0:
                result = json.loads(response['content'][0].get('text', '{}'))
            else:
                result = response
            if result.get("status") == "ACCEPTED":
                self.auth_token = result.get("auth_token")
                logging.info(f"Player {self.player_id} registered successfully")
                self.logger.info("PLAYER_REGISTERED", auth_token_received=bool(self.auth_token))
            else:
                logging.error(f"Player registration failed: {result}")
        except Exception as e:
            logging.error(f"Error registering player: {e}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--player-id", required=True)
    parser.add_argument("--league-id", default="league_2025_even_odd")
    parser.add_argument("--port", type=int, default=8101)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--league-manager", required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    player = PlayerAgent(args.player_id, args.league_id, args.strategy, args.league_manager, args.port)
    await player.register_with_league()
    import uvicorn
    uvicorn_config = uvicorn.Config(player.mcp_server.app, host="localhost", port=args.port, log_level="info")
    await uvicorn.Server(uvicorn_config).serve()

if __name__ == "__main__":
    asyncio.run(main())
