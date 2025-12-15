"""
Referee Agent - Template for Protocol V2.

Demonstrates modular architecture following Section 11.
Split into: main.py, handlers.py, game_logic.py
"""

import asyncio
import argparse
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from league_sdk import ConfigLoader, JsonLogger
from league_sdk.mcp_server import MCPServer
from league_sdk.game_rules.even_odd import EvenOddRules


class RefereeAgent:
    """Referee Agent for managing matches using modular architecture."""
    
    def __init__(self, referee_id: str, league_id: str):
        """Initialize referee with SDK configuration."""
        # Load configuration
        config_loader = ConfigLoader()
        self.system_config = config_loader.load_system()
        self.referee_config = config_loader.get_referee_by_id(referee_id)
        
        self.referee_id = referee_id
        self.league_id = league_id
        
        # Initialize logging  
        self.logger = JsonLogger(f"referee:{referee_id}", league_id=league_id)
        self.logger.info("REFEREE_INIT", referee_id=referee_id)
        
        # Game logic
        self.game = EvenOddRules()
        
        # MCP Server
        self.mcp_server = MCPServer(f"Referee-{referee_id}")
        self._setup_tools()
        
        logging.info(f"Referee {referee_id} initialized")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("start_match", self.start_match)
        # Additional tools would be defined in handlers.py
    
    async def start_match(self, args: dict) -> dict:
        """Start a match - simplified example."""
        match_id = args.get('match_id')
        self.logger.info("MATCH_STARTED", match_id=match_id)
        
        # Match logic would be in handlers.py
        return {"status": "STARTED", "match_id": match_id}


async def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--referee-id", required=True)
    parser.add_argument("--league-id", default="league_2025_even_odd")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    referee = RefereeAgent(args.referee_id, args.league_id)
    
    # Start MCP server
    import uvicorn
    uvicorn_config = uvicorn.Config(
        referee.mcp_server.app,
        host="localhost",
        port=args.port,
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
