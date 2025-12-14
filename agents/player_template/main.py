"""
Player Agent - Template for Protocol V2.

Demonstrates modular architecture following Section 11.
Split into: main.py, handlers.py, strategy.py
"""

import asyncio
import argparse
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from league_sdk import ConfigLoader, JsonLogger
from league_sdk.mcp_server import MCPServer
from league_sdk.mcp_client import MCPClient


class PlayerAgent:
    """Player Agent using modular architecture and SDK."""
    
    def __init__(self, player_id: str, league_id: str):
        """Initialize player with SDK configuration."""
        # Load configuration
        config_loader = ConfigLoader()
        self.system_config = config_loader.load_system()
        self.player_config = config_loader.get_player_by_id(player_id)
        
        self.player_id = player_id
        self.league_id = league_id
        self.auth_token = None
        
        # Initialize logging
        self.logger = JsonLogger(f"player:{player_id}", league_id=league_id)
        self.logger.info("PLAYER_INIT", player_id=player_id)
        
        #  Use your strategy config
        self.strategy = self.player_config.strategy  # "random", "always_even", etc.
        
        # MCP components
        self.mcp_server = MCPServer(f"Player-{player_id}")
        self.mcp_client = MCPClient()
        
        self._setup_tools()
        logging.info(f"Player {player_id} initialized with strategy: {self.strategy}")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("notify_round", self.notify_round)
        self.mcp_server.register_tool("notify_standings", self.notify_standings)
        # Additional tools would be in handlers.py
    
    async def notify_round(self, args: dict) -> dict:
        """Handle round announcement - simplified example."""
       round_id = args.get('round_id')
        self.logger.info("ROUND_NOTIFIED", round_id=round_id)
        return {"status": "ACK"}
    
    async def notify_standings(self, args: dict) -> dict:
        """Handle standings update - simplified example."""
        standings = args.get('standings', [])
        self.logger.info("STANDINGS_RECEIVED", count=len(standings))
        return {"status": "ACK"}


async def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--player-id", required=True)
    parser.add_argument("--league-id", default="league_2025_even_odd")
    parser.add_argument("--port", type=int, default=8101)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    player = PlayerAgent(args.player_id, args.league_id)
    
    # Start MCP server
    import uvicorn
    uvicorn_config = uvicorn.Config(
        player.mcp_server.app,
        host="localhost",
        port=args.port,
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
