"""Referee - Manages individual match execution."""
import asyncio
import argparse
import logging
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from utils.mcp_server import MCPServer
from utils.mcp_client import MCPClient
from utils.helpers import get_iso_timestamp, generate_conversation_id, setup_logging
from utils.schemas import GameInvitation, ChooseParityCall, GameOver, GameResult
from game_rules.even_odd import EvenOddRules
from datetime import datetime, timedelta, timezone
import uvicorn
import json


class Referee:
    """Referee MCP Server for match execution."""
    
    def __init__(self, port: int):
        self.port = port
        self.referee_id = None  # Assigned after registration
        self.auth_token = None  # Received after registration
        self.league_manager_endpoint = None
        self.mcp_server = MCPServer(f"Referee-{port}")
        self.mcp_client = MCPClient(timeout=35)
        self.game_rules = EvenOddRules()
        self.matches = {}
        self._setup_tools()
        logging.info(f"Referee initialized on port {port}")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("start_match", self.start_match)
        self.mcp_server.register_tool("notify_league_completed", self.notify_league_completed)
    
    async def register_with_league(self, league_manager_url: str):
        """Register referee with League Manager before accepting matches."""
        self.league_manager_endpoint = league_manager_url
        
        referee_meta = {
            "display_name": f"Referee-{self.port}",
            "version": "1.0.0",
            "game_types": ["even_odd"],
            "contact_endpoint": f"http://localhost:{self.port}/mcp",
            "max_concurrent_matches": 2
        }
        
        logging.info(f"Registering referee with league manager at {league_manager_url}")
        
        try:
            result = await self.mcp_client.call_tool(
                league_manager_url,
                "register_referee",
                {"referee_meta": referee_meta}
            )
            
            result_text = result.get('content', [{}])[0].get('text', '{}')
            result_data = json.loads(result_text)
            
            if result_data.get('status') == 'ACCEPTED':
                self.referee_id = result_data['referee_id']
                self.auth_token = result_data['auth_token']
                logging.info(f"Referee registration successful: {self.referee_id}")
                logging.info(f"Auth token received: {self.auth_token[:20]}...")
                return True
            else:
                logging.error(f"Referee registration failed: {result_data.get('reason')}")
                return False
        except Exception as e:
            logging.error(f"Failed to register referee: {e}")
            return False
    
    async def start_match(self, args: dict) -> dict:
        """Execute a complete match."""
        match_id = args['match_id']
        round_id = args['round_id']
        player_A_id = args['player_A_id']
        player_B_id = args['player_B_id']
        player_A_endpoint = args['player_A_endpoint']
        player_B_endpoint = args['player_B_endpoint']
        league_id = args['league_id']
        
        logging.info(f"Starting match {match_id}: {player_A_id} vs {player_B_id}")
        
        conv_id = generate_conversation_id(match_id)
        
        # Step 1: Send invitations
        invite_A = await self._send_invitation(
            player_A_id, player_B_id, match_id, round_id, league_id, 
            "PLAYER_A", player_A_endpoint, conv_id
        )
        invite_B = await self._send_invitation(
            player_B_id, player_A_id, match_id, round_id, league_id,
            "PLAYER_B", player_B_endpoint, conv_id
        )
        
        if not (invite_A and invite_B):
            return await self._technical_loss(match_id, player_A_id, player_B_id, "Invitation timeout")
        
        # Step 2: Collect choices
        choice_A = await self._collect_parity_choice(player_A_id, player_A_endpoint, match_id, round_id, league_id, conv_id)
        choice_B = await self._collect_parity_choice(player_B_id, player_B_endpoint, match_id, round_id, league_id, conv_id)
        
        if not choice_A or not choice_B:
            return await self._technical_loss(match_id, player_A_id, player_B_id, "Choice timeout")
        
        # Step 3: Draw number and determine winner
        drawn_number = self.game_rules.draw_number()
        winner, reason = self.game_rules.determine_winner(choice_A, choice_B, drawn_number)
        
        # Step 4: Calculate scores
        temp_score = self.game_rules.calculate_score(winner)
        score = {player_A_id: temp_score["PLAYER_A"], player_B_id: temp_score["PLAYER_B"]}
        
        winner_id = player_A_id if winner == "PLAYER_A" else (player_B_id if winner == "PLAYER_B" else None)
        
        logging.info(f"Match {match_id} complete: Winner={winner_id}, Number={drawn_number}")
        
        # Step 5: Notify players
        await self._notify_game_over(player_A_id, player_A_endpoint, match_id, round_id, league_id, 
                                     winner_id, drawn_number, {player_A_id: choice_A, player_B_id: choice_B}, reason)
        await self._notify_game_over(player_B_id, player_B_endpoint, match_id, round_id, league_id,
                                     winner_id, drawn_number, {player_A_id: choice_A, player_B_id: choice_B}, reason)
        
        # Step 6: Report results to league manager
        league_manager_endpoint = self.league_manager_endpoint or args.get('league_manager_endpoint', 'http://localhost:8000/mcp')
        try:
            await self.mcp_client.call_tool(league_manager_endpoint, "report_match_result", {
                "protocol": "league.v2",
                "message_type": "MATCH_RESULT_REPORT",
                "sender": f"referee:{self.referee_id}",
                "timestamp": get_iso_timestamp(),
                "auth_token": self.auth_token,
                "league_id": league_id,
                "round_id": round_id,
                "match_id": match_id,
                "game_type": "even_odd",
                "result": {
                    "winner": winner_id,
                    "score": score,
                    "details": {
                        "drawn_number": drawn_number,
                        "choices": {player_A_id: choice_A, player_B_id: choice_B},
                        "reason": reason
                    }
                }
            })
            logging.info(f"Match {match_id} result reported to league manager")
        except Exception as e:
            logging.error(f"Failed to report match {match_id} to league manager: {e}")
        
        return {"status": "OK", "winner": winner_id, "score": score}
    
    async def _send_invitation(self, player_id, opponent_id, match_id, round_id, league_id, role, endpoint, conv_id):
        """Send game invitation to player."""
        params = GameInvitation(
            protocol="league.v2",
            message_type="GAME_INVITATION",
            sender=f"referee:{self.referee_id}",
            timestamp=get_iso_timestamp(),
            conversation_id=conv_id,
            auth_token=self.auth_token,
            league_id=league_id,
            round_id=round_id,
            match_id=match_id,
            game_type="even_odd",
            role_in_match=role,
            opponent_id=opponent_id
        ).dict()
        
        try:
            result = asyncio.run(self.mcp_client.call_tool(endpoint, "handle_game_invitation", params))
            return result
        except Exception as e:
            logging.error(f"Failed to send invitation to {player_id}: {e}")
            return None
    
    async def _collect_parity_choice(self, player_id, endpoint, match_id, round_id, league_id, conv_id):
        """Collect parity choice from player."""
        
        deadline_dt = datetime.now(timezone.utc) + timedelta(seconds=30)
        deadline = deadline_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        params = ChooseParityCall(
            protocol="league.v2",
            message_type="CHOOSE_PARITY_CALL",
            sender=f"referee:{self.referee_id}",
            timestamp=get_iso_timestamp(),
            conversation_id=conv_id,
            auth_token=self.auth_token,
            league_id=league_id,
            round_id=round_id,
            match_id=match_id,
            player_id=player_id,
            game_type="even_odd",
            context={"opponent_id": ""},
            deadline=deadline
        ).dict()
        
        try:
            result = asyncio.run(self.mcp_client.call_tool(endpoint, "choose_parity", params))
            choice = result.get('parity_choice')
            logging.info(f"Player {player_id} chose: {choice}")
            return choice
        except Exception as e:
            logging.error(f"Failed to collect choice from {player_id}: {e}")
            return None
    
    async def _notify_game_over(self, player_id, endpoint, match_id, round_id, league_id, winner_id, drawn_number, choices, reason):
        """Send GAME_OVER notification."""
        conv_id = generate_conversation_id(f"{match_id}-end")
        
        result = GameResult(
            status="WIN" if winner_id else "DRAW",
            winner_player_id=winner_id,
            drawn_number=drawn_number,
            number_parity=self.game_rules.determine_parity(drawn_number),
            choices=choices,
            reason=reason
        )
        
        params = GameOver(
            protocol="league.v2",
            message_type="GAME_OVER",
            sender=f"referee:{self.referee_id}",
            timestamp=get_iso_timestamp(),
            conversation_id=conv_id,
            auth_token=self.auth_token,
            league_id=league_id,
            round_id=round_id,
            match_id=match_id,
            game_type="even_odd",
            game_result=result
        ).dict()
        
        try:
            await self.mcp_client.call_tool(endpoint, "notify_match_result", params)
            logging.info(f"GAME_OVER sent to {player_id}")
        except Exception as e:
            logging.error(f"Failed to notify {player_id}: {e}")
    
    async def _technical_loss(self, match_id, player_A_id, player_B_id, reason):
        """Handle technical loss."""
        logging.warning(f"Technical loss in {match_id}: {reason}")
        return {"status": "TECHNICAL_LOSS", "reason": reason}
    
    async def notify_league_completed(self, args: dict) -> dict:
        """Receive league completion notification for graceful shutdown."""
        logging.info("League completed - referee shutting down")
        return {"status": "ok"}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--league", default="http://localhost:8000/mcp", help="League manager URL")
    args = parser.parse_args()
    
    # Setup logging with file output
    setup_logging(
        log_dir='logs',
        log_file=f'referee_{args.port}.log',
        level='INFO'
    )
    
    referee = Referee(args.port)
    
    # Create uvicorn config
    uvicorn_config = uvicorn.Config(
        referee.mcp_server.app,
        host="localhost",
        port=args.port,
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    
    # Register with league manager and run server concurrently
    logging.info("Starting referee registration and server...")
    await asyncio.gather(
        server.serve(),
        referee.register_with_league(args.league)
    )


if __name__ == "__main__":
    asyncio.run(main())

