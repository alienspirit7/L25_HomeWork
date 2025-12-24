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
from league_sdk.mcp_client import MCPClient
from league_sdk.game_rules.even_odd import EvenOddRules
from handlers import RefereeHandlers


class RefereeAgent:
    """Referee Agent for managing matches using modular architecture."""
    
    def __init__(self, referee_id: str, league_id: str, league_manager_url: str, port: int):
        """Initialize referee with SDK configuration."""
        # Load configuration
        config_loader = ConfigLoader()
        self.system_config = config_loader.load_system()
        self.referee_config = config_loader.get_referee_by_id(referee_id)
        
        self.referee_id = referee_id
        self.league_id = league_id
        self.league_manager_url = league_manager_url
        self.port = port
        self.auth_token = None
        
        # Initialize logging  
        self.logger = JsonLogger(f"referee:{referee_id}", league_id=league_id)
        self.logger.info("REFEREE_INIT", referee_id=referee_id)
        
        # Game logic
        self.game = EvenOddRules()
        
        # MCP components
        self.mcp_server = MCPServer(f"Referee-{referee_id}")
        self.mcp_client = MCPClient()
        
        # Initialize handlers with match execution logic
        self.handlers = RefereeHandlers(self)
        self._setup_tools()
        
        # Store league manager endpoint for result reporting
        self.league_manager_endpoint = league_manager_url
        
        logging.info(f"Referee {referee_id} initialized")
    
    def _setup_tools(self):
        """Register MCP tools."""
        # Use handler's start_match which has full match execution logic
        self.mcp_server.register_tool("start_match", self.handlers.start_match)

    
    async def register_with_league(self):
        """Register this referee with the league manager."""
        try:
            import json
            referee_meta = {
                "display_name": f"Referee-{self.referee_id}",
                "version": "2.1.0",
                "game_types": ["even_odd"],
                "contact_endpoint": f"http://localhost:{self.port}/mcp",
                "max_concurrent_matches": 1
            }
            
            response = await self.mcp_client.call_tool(
                self.league_manager_url,
                "register_referee",
                {"referee_meta": referee_meta}
)
            
            # Parse MCP response wrapper
            if 'content' in response and len(response['content']) > 0:
                result_text = response['content'][0].get('text', '{}')
                result = json.loads(result_text)
            else:
                result = response
            
            if result.get("status") == "ACCEPTED":
                self.auth_token = result.get("auth_token")
                logging.info(f"Referee {self.referee_id} registered successfully")
                self.logger.info("REFEREE_REGISTERED", auth_token_received=bool(self.auth_token))
            else:
                logging.error(f"Referee registration failed: {result}")
        except Exception as e:
            logging.error(f"Error registering referee: {e}")


async def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--referee-id", required=True)
    parser.add_argument("--league-id", default="league_2025_even_odd")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--league-manager", required=True, help="League manager MCP endpoint URL")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    referee = RefereeAgent(args.referee_id, args.league_id, args.league_manager, args.port)
    
    # Register with league manager
    await referee.register_with_league()
    
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
