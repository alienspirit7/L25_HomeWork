"""Referee Agent - Message Handlers.

This module contains all message handling logic for the referee agent.
Handles invitations, parity collection, and result reporting.
"""

import logging
from typing import Dict, Optional
from league_sdk.helpers import get_iso_timestamp, generate_conversation_id
from league_sdk.mcp_client import MCPClient


class RefereeHandlers:
    """Message handlers for Referee Agent."""
    
    def __init__(self, referee):
        """Initialize handlers with reference to referee agent."""
        self.referee = referee
        self.mcp_client = MCPClient()
    
    async def start_match(self, args: dict) -> dict:
        """
        Handle start_match request from League Manager.
        
        Args:
            args: {
                'match_id': str,
                'round_id': int, 
                'player_A_id': str,
                'player_B_id': str,
                'player_A_endpoint': str,
                'player_B_endpoint': str
            }
        
        Returns:
            {'status': 'STARTED', 'match_id': str}
        """
        match_id = args.get('match_id')
        round_id = args.get('round_id')
        player_A_id = args.get('player_A_id')
        player_B_id = args.get('player_B_id')
        player_A_endpoint = args.get('player_A_endpoint')
        player_B_endpoint = args.get('player_B_endpoint')
        
        self.referee.logger.info(
            "MATCH_START",
            match_id=match_id,
            round_id=round_id,
            players=[player_A_id, player_B_id]
        )
        
        # Send game invitations
        await self._send_invitations(
            match_id, round_id, player_A_id, player_B_id,
            player_A_endpoint, player_B_endpoint
        )
        
        # Collect parity choices
        choices = await self._collect_parity_choices(
            match_id, player_A_id, player_B_id,
            player_A_endpoint, player_B_endpoint
        )
        
        # Determine winner using game logic
        from game_logic import execute_match
        result = execute_match(
            player_A_id, player_B_id,
            choices.get(player_A_id), choices.get(player_B_id),
            self.referee.game
        )
        
        # Send game over messages
        await self._send_game_over(
            match_id, player_A_id, player_B_id,
            player_A_endpoint, player_B_endpoint,
            result
        )
        
        # Report result to League Manager
        await self._report_match_result(match_id, round_id, result)
        
        self.referee.logger.info(
            "MATCH_COMPLETE",
            match_id=match_id,
            winner=result['winner']
        )
        
        return {"status": "STARTED", "match_id": match_id}
    
    async def _send_invitations(
        self, match_id: str, round_id: int,
        player_A_id: str, player_B_id: str,
        player_A_endpoint: str, player_B_endpoint: str
    ):
        """Send GAME_INVITATION to both players."""
        invitation_A = self._create_invitation(
            match_id, round_id, player_A_id, player_B_id
        )
        invitation_B = self._create_invitation(
            match_id, round_id, player_B_id, player_A_id
        )
        
        # Send invitations concurrently
        await self.mcp_client.call_tool(
            player_A_endpoint, "receive_game_invitation", invitation_A
        )
        await self.mcp_client.call_tool(
            player_B_endpoint, "receive_game_invitation", invitation_B
        )
        
        self.referee.logger.info(
            "INVITATIONS_SENT",
            match_id=match_id,
            players=[player_A_id, player_B_id]
        )
    
    async def _collect_parity_choices(
        self, match_id: str,
        player_A_id: str, player_B_id: str,
        player_A_endpoint: str, player_B_endpoint: str
    ) -> Dict[str, str]:
        """Collect parity choices from both players."""
        call_msg_A = self._create_parity_call(match_id, player_A_id)
        call_msg_B = self._create_parity_call(match_id, player_B_id)
        
        # Call both players
        response_A = await self.mcp_client.call_tool(
            player_A_endpoint, "choose_parity", call_msg_A
        )
        response_B = await self.mcp_client.call_tool(
            player_B_endpoint, "choose_parity", call_msg_B
        )
        
        choices = {
            player_A_id: response_A.get('parity_choice', 'even'),
            player_B_id: response_B.get('parity_choice', 'odd')
        }
        
        self.referee.logger.info(
            "CHOICES_COLLECTED",
            match_id=match_id,
            choices=choices
        )
        
        return choices
    
    async def _send_game_over(
        self, match_id: str,
        player_A_id: str, player_B_id: str,
        player_A_endpoint: str, player_B_endpoint: str,
        result: dict
    ):
        """Send GAME_OVER message to both players."""
        game_over_A = self._create_game_over(match_id, player_A_id, result)
        game_over_B = self._create_game_over(match_id, player_B_id, result)
        
        await self.mcp_client.call_tool(
            player_A_endpoint, "receive_game_over", game_over_A
        )
        await self.mcp_client.call_tool(
            player_B_endpoint, "receive_game_over", game_over_B
        )
    
    async def _report_match_result(
        self, match_id: str, round_id: int, result: dict
    ):
        """Report match result to League Manager."""
        league_endpoint = self.referee.league_manager_endpoint
        
        report = {
            "protocol": "league.v2",
            "message_type": "MATCH_RESULT_REPORT",
            "sender": f"referee:{self.referee.referee_id}",
            "auth_token": self.referee.auth_token,
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"report-{match_id}"),
            "league_id": self.referee.league_id,
            "round_id": round_id,
            "match_id": match_id,
            "game_type": "even_odd",
            "result": result
        }
        
        await self.mcp_client.call_tool(
            league_endpoint, "report_match_result", report
        )
    
    def _create_invitation(
        self, match_id: str, round_id: int,
        player_id: str, opponent_id: str
    ) -> dict:
        """Create GAME_INVITATION message."""
        # Determine role based on player position (simple heuristic)
        # In practice, this should be passed as parameter
        role_in_match = "PLAYER_A"  # Could be determined by match setup
        
        return {
            "protocol": "league.v2",
            "message_type": "GAME_INVITATION",
            "sender": f"referee:{self.referee.referee_id}",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"invite-{match_id}-{player_id}"),
            "auth_token": self.referee.auth_token,
            "league_id": self.referee.league_id,
            "round_id": round_id,
            "match_id": match_id,
            "game_type": "even_odd",
            "role_in_match": role_in_match,
            "opponent_id": opponent_id
        }
    
    def _create_parity_call(self, match_id: str, player_id: str) -> dict:
        """Create CHOOSE_PARITY_CALL message."""
        from datetime import datetime, timedelta
        
        # Calculate deadline (30 seconds from now as per spec timeout)
        deadline = datetime.utcnow() + timedelta(seconds=30)
        deadline_str = deadline.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return {
            "protocol": "league.v2",
            "message_type": "CHOOSE_PARITY_CALL",
            "sender": f"referee:{self.referee.referee_id}",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"parity-{match_id}-{player_id}"),
            "auth_token": self.referee.auth_token,
            "league_id": self.referee.league_id,
            "match_id": match_id,
            "player_id": player_id,
            "game_type": "even_odd",
            "context": {
                "opponent_id": "",  # Should be passed as parameter
                "round_id": 0,  # Should be passed as parameter
                "your_standings": {
                    "wins": 0,
                    "losses": 0,
                    "draws": 0
                }
            },
            "deadline": deadline_str
        }
    
    def _create_game_over(
        self, match_id: str, player_id: str, result: dict
    ) -> dict:
        """Create GAME_OVER message matching specification."""
        details = result.get('details', {})
        winner = result.get('winner')
        
        # Determine status
        if winner is None:
            status = "DRAW"
        else:
            status = "WIN"
        
        return {
            "protocol": "league.v2",
            "message_type": "GAME_OVER",
            "sender": f"referee:{self.referee.referee_id}",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"game-over-{match_id}"),
            "auth_token": self.referee.auth_token,
            "match_id": match_id,
            "game_type": "even_odd",
            "game_result": {
                "status": status,
                "winner_player_id": winner if winner else None,
                "drawn_number": details.get('drawn_number'),
                "number_parity": details.get('parity'),
                "choices": details.get('choices', {}),
                "reason": details.get('reason', '')
            }
        }

