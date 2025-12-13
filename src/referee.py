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
from game_rules.even_odd import EvenOddRules
import uvicorn


class Referee:
    """Referee MCP Server for match execution."""
    
    def __init__(self, port: int):
        self.port = port
        self.mcp_server = MCPServer(f"Referee-{port}")
        self.mcp_client = MCPClient(timeout=35)
        self.game_rules = EvenOddRules()
        self.matches = {}
        self._setup_tools()
        logging.info(f"Referee initialized on port {port}")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("start_match", self.start_match)
    
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
        league_manager_endpoint = args.get('league_manager_endpoint', 'http://localhost:8000/mcp')
        try:
            await self.mcp_client.call_tool(league_manager_endpoint, "report_match_result", {
                "match_id": match_id,
                "winner": winner_id,
                "score": score,
                "details": {
                    "drawn_number": drawn_number,
                    "choices": {player_A_id: choice_A, player_B_id: choice_B},
                    "reason": reason
                }
            })
            logging.info(f"Match {match_id} result reported to league manager")
        except Exception as e:
            logging.error(f"Failed to report match {match_id} to league manager: {e}")
        
        return {"status": "OK", "winner": winner_id, "score": score}
    
    async def _send_invitation(self, player_id, opponent_id, match_id, round_id, league_id, role, endpoint, conv_id):
        """Send game invitation to player."""
        try:
            result = await self.mcp_client.call_tool(endpoint, "handle_game_invitation", {
                "protocol": "league.v1",
                "message_type": "GAME_INVITATION",
                "league_id": league_id,
                "round_id": round_id,
                "match_id": match_id,
                "conversation_id": conv_id,
                "sender": f"referee:{self.port}",
                "timestamp": get_iso_timestamp(),
                "player_id": player_id,
                "game_type": "even_odd",
                "role_in_match": role,
                "opponent_id": opponent_id
            })
            return result.get('content', [{}])[0].get('text', '{}')
        except:
            return None
    
    async def _collect_parity_choice(self, player_id, endpoint, match_id, round_id, league_id, conv_id):
        """Collect parity choice from player."""
        for attempt in range(3):
            try:
                result = await self.mcp_client.call_tool(endpoint, "choose_parity", {
                    "protocol": "league.v1",
                    "message_type": "CHOOSE_PARITY_CALL",
                    "league_id": league_id,
                    "round_id": round_id,
                    "match_id": match_id,
                    "conversation_id": conv_id,
                    "sender": f"referee:{self.port}",
                    "timestamp": get_iso_timestamp(),
                    "player_id": player_id,
                    "game_type": "even_odd",
                    "context": {},
                    "deadline": get_iso_timestamp()
                })
                
                import json
                response = json.loads(result.get('content', [{}])[0].get('text', '{}'))
                choice = response.get('parity_choice')
                
                is_valid, _ = self.game_rules.validate_choice(choice)
                if is_valid:
                    return choice
            except:
                continue
        return None
    
    async def _notify_game_over(self, player_id, endpoint, match_id, round_id, league_id, winner_id, drawn_number, choices, reason):
        """Send GAME_OVER notification."""
        try:
            await self.mcp_client.call_tool(endpoint, "notify_match_result", {
                "protocol": "league.v1",
                "message_type": "GAME_OVER",
                "league_id": league_id,
                "round_id": round_id,
                "match_id": match_id,
                "sender": f"referee:{self.port}",
                "timestamp": get_iso_timestamp(),
                "game_type": "even_odd",
                "game_result": {
                    "status": "WIN" if winner_id else "DRAW",
                    "winner_player_id": winner_id,
                    "drawn_number": drawn_number,
                    "number_parity": self.game_rules.determine_parity(drawn_number),
                    "choices": choices,
                    "reason": reason
                }
            })
        except Exception as e:
            logging.error(f"Failed to notify {player_id}: {e}")
    
    async def _technical_loss(self, match_id, player_A_id, player_B_id, reason):
        """Handle technical loss."""
        logging.warning(f"Technical loss in {match_id}: {reason}")
        return {"status": "TECHNICAL_LOSS", "reason": reason}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    
    # Setup logging with file output
    setup_logging(
        log_dir='logs',
        log_file=f'referee_{args.port}.log',
        level='INFO'
    )
    
    referee = Referee(args.port)
    uvicorn.run(referee.mcp_server.app, host="localhost", port=args.port)


if __name__ == "__main__":
    main()
