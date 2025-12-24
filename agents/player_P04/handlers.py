"""Player Agent - Message Handlers.

This module contains all message handling logic for the player agent.
Handles registration, invitations, game moves, and notifications.
"""

import logging
from typing import Dict
from league_sdk.helpers import get_iso_timestamp
from league_sdk.mcp_client import MCPClient


class PlayerHandlers:
    """Message handlers for Player Agent."""
    
    def __init__(self, player):
        """Initialize handlers with reference to player agent."""
        self.player = player
        self.mcp_client = MCPClient()
    
    async def register_with_league(self, league_endpoint: str) -> Dict:
        """
        Register player with League Manager.
        
        Args:
            league_endpoint: League Manager endpoint URL
        
        Returns:
            Registration response with player_id and auth_token
        """
        registration_request = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_REGISTER_REQUEST",
            "sender": f"player:{self.player.player_id}",
            "timestamp": get_iso_timestamp(),
            "player_meta": {
                "display_name": self.player.player_config.display_name,
                "protocol_version": "2.1.0",
                "agent_version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": self.player.player_config.endpoint
            }
        }
        
        response = await self.mcp_client.call_tool(
            league_endpoint, "register_player", registration_request
        )
        
        if response.get('status') == 'ACCEPTED':
            self.player.player_id = response['player_id']
            self.player.auth_token = response['auth_token']
            self.player.logger.info(
                "REGISTRATION_SUCCESS",
                player_id=response['player_id']
            )
        else:
            self.player.logger.error(
                "REGISTRATION_FAILED",
                reason=response.get('reason', 'Unknown')
            )
        
        return response
    
    async def receive_game_invitation(self, args: dict) -> dict:
        """
        Handle GAME_INVITATION from referee.
        
        Args:
            args: Invitation message with match details
        
        Returns:
            {'status': 'ACK'}
        """
        match_id = args.get('match_id')
        opponent_id = args.get('opponent_id')
        
        self.player.logger.info(
            "GAME_INVITATION_RECEIVED",
            match_id=match_id,
            opponent_id=opponent_id
        )
        
        # Store match info
        self.player.current_match = {
            "match_id": match_id,
            "opponent_id": opponent_id,
            "round_id": args.get('round_id')
        }
        
        return {"status": "ACK"}
    
    async def choose_parity(self, args: dict) -> dict:
        """
        Handle CHOOSE_PARITY_CALL from referee.
        
        Args:
            args: Parity call message
        
        Returns:
            {'parity_choice': str}
        """
        match_id = args.get('match_id')
        
        # Use strategy module to determine choice
        from strategy import determine_parity_choice
        choice = determine_parity_choice(
            self.player.strategy,
            self.player.current_match
        )
        
        self.player.logger.info(
            "PARITY_CHOICE_MADE",
            match_id=match_id,
            choice=choice
        )
        
        return {
            "protocol": "league.v2",
            "message_type": "CHOOSE_PARITY_RESPONSE",
            "sender": f"player:{self.player.player_id}",
            "timestamp": get_iso_timestamp(),
            "match_id": match_id,
            "parity_choice": choice
        }
    
    async def receive_game_over(self, args: dict) -> dict:
        """
        Handle GAME_OVER message from referee.

        Args:
            args: Game over message with new game_result structure.

        Returns:
            {'status': 'ACK', 'received': True}
        """
        match_id = args.get('match_id')
        game_result = args.get('game_result', {})
        
        # Extract result from new game_result structure
        status = game_result.get('status')  # "WIN", "DRAW", "TECHNICAL_LOSS"
        winner_player_id = game_result.get('winner_player_id')
        drawn_number = game_result.get('drawn_number')
        choices = game_result.get('choices', {})
        reason = game_result.get('reason', '')
        
        # Determine if this player won
        won = (winner_player_id == self.player.player_id)
        is_draw = (status == "DRAW")
        
        self.player.logger.info(
            "GAME_OVER_RECEIVED",
            match_id=match_id,
            status=status,
            winner=winner_player_id,
            won=won,
            is_draw=is_draw,
            drawn_number=drawn_number,
            reason=reason
        )
        
        # Update internal stats (optional)
        if won:
            logging.info(f"Player {self.player.player_id} WON match {match_id}")
        elif is_draw:
            logging.info(f"Player {self.player.player_id} DREW match {match_id}")
        else:
            logging.info(f"Player {self.player.player_id} LOST match {match_id}")
        
        # Clear current match
        self.player.current_match = None
        
        return {"status": "ACK", "received": True}
    
    async def notify_round(self, args: dict) -> dict:
        """
        Handle round announcement from League Manager.
        
        Args:
            args: Round notification message
        
        Returns:
            {'status': 'ACK'}
        """
        round_id = args.get('round_id')
        
        self.player.logger.info(
            "ROUND_NOTIFIED",
            round_id=round_id
        )
        
        return {"status": "ACK"}
    
    async def notify_standings(self, args: dict) -> dict:
        """
        Handle standings update from League Manager.
        
        Args:
            args: Standings notification message
        
        Returns:
            {'status': 'ACK'}
        """
        standings = args.get('standings', [])
        
        # Find our position
        our_standing = next(
            (s for s in standings if s.get('player_id') == self.player.player_id),
            None
        )
        
        self.player.logger.info(
            "STANDINGS_RECEIVED",
            total_players=len(standings),
            our_rank=our_standing.get('rank') if our_standing else None,
            our_points=our_standing.get('points') if our_standing else None
        )
        
        return {"status": "ACK"}
    
    async def query_league(
        self, query_type: str, query_params: dict = None
    ) -> dict:
        """
        Send LEAGUE_QUERY to League Manager.
        
        Args:
            query_type: Type of query (GET_STANDINGS, GET_SCHEDULE, etc.)
            query_params: Optional parameters for the query
        
        Returns:
            Query response from League Manager
        """
        query_request = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_QUERY",
            "sender": f"player:{self.player.player_id}",
            "auth_token": self.player.auth_token,
            "timestamp": get_iso_timestamp(),
            "league_id": self.player.league_id,
            "query_type": query_type,
            "query_params": query_params or {}
        }
        
        response = await self.mcp_client.call_tool(
            self.player.league_manager_endpoint,
            "handle_league_query",
            query_request
        )
        
        self.player.logger.info(
            "LEAGUE_QUERY_SENT",
            query_type=query_type,
            success=response.get('success', False)
        )
        
        return response
