"""League Manager - Message handler functions."""
import logging
from typing import Dict
from league_sdk import StandingsRepository
from league_sdk.helpers import (
    generate_auth_token,
    generate_conversation_id,
    get_iso_timestamp,
    calculate_standings,
)


class LeagueHandlers:
    """Message handlers for League Manager."""
    
    def __init__(self, manager):
        """Initialize handlers with reference to manager."""
        self.manager = manager
    
    async def register_referee(self, args: dict) -> dict:
        """Handle referee registration (Protocol v2)."""
        referee_meta = args.get('referee_meta', {})
        
        # Validate required fields
        required = ['display_name', 'version', 'game_types', 'contact_endpoint']
        for field in required:
            if field not in referee_meta:
                return self.manager.mcp_server.create_league_error(
                    "E003", "MISSING_REQUIRED_FIELD",
                    context={"missing_field": field}
                )
        
        # Generate referee ID
        self.manager.referee_counter += 1
        referee_id = f"REF{self.manager.referee_counter:02d}"
        
        # Generate auth token
        auth_token = generate_auth_token("referee", referee_id)
        
        # Store referee info
        self.manager.referees[referee_id] = {
            "referee_id": referee_id,
            "display_name": referee_meta['display_name'],
            "endpoint": referee_meta['contact_endpoint'],
            "game_types": referee_meta['game_types'],
            "max_concurrent": referee_meta.get('max_concurrent_matches', 1),
            "registered_at": get_iso_timestamp()
        }
        self.manager.referee_tokens[referee_id] = auth_token
        
        logging.info(f"Referee registered: {referee_id} - {referee_meta['display_name']}")
        
        return {
            "message_type": "REFEREE_REGISTER_RESPONSE",
            "status": "ACCEPTED",
            "referee_id": referee_id,
            "auth_token": auth_token,
            "reason": None
        }
    
    async def register_player(self, args: dict) -> dict:
        """Handle player registration with auth token."""
        if self.manager.registration_closed:
            return self.manager.mcp_server.create_league_error(
                "E018", "REGISTRATION_CLOSED",
                context={"registration_timeout": self.manager.registration_timeout}
            )
        
        player_meta = args.get('player_meta', args)
        
        # Validate protocol version (v2)
        protocol_version = player_meta.get('protocol_version', '1.0.0')
        if not protocol_version.startswith('2.'):
            return self.manager.mcp_server.create_league_error(
                "E018", "PROTOCOL_VERSION_MISMATCH",
                context={
                    "provided_version": protocol_version,
                    "required_version": "2.1.0"
                }
            )
        
        # Validate game type
        game_types = player_meta.get('game_types', [])
        if self.manager.league_config.game_type not in game_types:
            return {
                "message_type": "LEAGUE_REGISTER_RESPONSE",
                "status": "REJECTED",
                "reason": "Game type not supported"
            }
        
        # Generate player ID and auth token
        self.manager.player_counter += 1
        player_id = f"P{self.manager.player_counter:02d}"
        auth_token = generate_auth_token("player", player_id)
        
        # Store player info
        self.manager.players[player_id] = {
            "player_id": player_id,
            "display_name": player_meta.get('display_name', f"Player {player_id}"),
            "endpoint": player_meta['contact_endpoint'],
            "registered_at": get_iso_timestamp()
        }
        self.manager.player_tokens[player_id] = auth_token
        
        logging.info(f"Player registered: {player_id} - {self.manager.players[player_id]['display_name']}")
        
        return {
            "message_type": "LEAGUE_REGISTER_RESPONSE",
            "status": "ACCEPTED",
            "player_id": player_id,
            "auth_token": auth_token,
            "league_id": self.manager.league_id,
            "reason": None
        }
    
    async def report_match_result(self, args: dict) -> dict:
        """Receive match result from referee."""
        # Validate auth_token
        sender = args.get('sender', '')
        auth_token = args.get('auth_token', '')
        
        if not self.manager._validate_auth_token(sender, auth_token):
            logging.warning(f"Invalid auth token from {sender}")
            return self.manager.mcp_server.create_league_error(
                "E012", "AUTH_TOKEN_INVALID",
                context={"sender": sender}
            )
        
        # Extract result data from V2 structure
        match_id = args.get('match_id')
        result = args.get('result', {})
        
        self.manager.results[match_id] = {
            "winner": result.get('winner'),
            "score": result.get('score', {}),
            "details": result.get('details', {})
        }
        self.manager.completed_matches.add(match_id)
        logging.info(f"Match result recorded: {match_id} ({len(self.manager.completed_matches)}/{self.manager.expected_matches})")
        self.manager._save_state()
        
        # Check if round is complete
        await self.manager.scheduler.check_round_completion(match_id)
        
        return {"status": "OK"}
    
    async def get_standings(self, args: dict) -> dict:
        """Calculate and return standings."""
        standings = calculate_standings(self.manager.results)
        return {"standings": standings}
    
    async def handle_league_query(self, args: dict) -> dict:
        """
        Handle LEAGUE_QUERY requests from players or referees.
        Supports: GET_STANDINGS, GET_SCHEDULE, GET_NEXT_MATCH, GET_PLAYER_STATS.
        """
        # Validate auth token
        sender = args.get('sender', '')
        auth_token = args.get('auth_token', '')
        
        if not self.manager._validate_auth_token(sender, auth_token):
            return self.manager.mcp_server.create_league_error(
                "E012", "AUTH_TOKEN_INVALID",
                original_message_type="LEAGUE_QUERY",
                context={"sender": sender}
            )
        
        query_type = args.get('query_type', '')
        query_params = args.get('query_params', {})
        conversation_id = args.get('conversation_id', generate_conversation_id("query"))
        
        # Process query based on type
        success = True
        data = {}
        error = None
        
        try:
            if query_type == "GET_STANDINGS":
                standings = calculate_standings(self.manager.results)
                # Add display names
                for entry in standings:
                    player_info = self.manager.players.get(entry['player_id'], {})
                    entry['display_name'] = player_info.get('display_name', entry['player_id'])
                data = {"standings": standings}
            
            elif query_type == "GET_SCHEDULE":
                schedule_data = []
                for player_A, player_B, round_id, match_num in self.manager.schedule:
                    match_id = f"R{round_id}M{match_num}"
                    schedule_data.append({
                        "match_id": match_id,
                        "round_id": round_id,
                        "player_A_id": player_A,
                        "player_B_id": player_B,
                        "completed": match_id in self.manager.completed_matches
                    })
                data = {"schedule": schedule_data, "total_matches": len(self.manager.schedule)}
            
            elif query_type == "GET_NEXT_MATCH":
                player_id = query_params.get('player_id', '')
                next_match = self._find_next_match(player_id)
                data = {"next_match": next_match} if next_match else {"next_match": None, "message": "No upcoming matches"}
            
            elif query_type == "GET_PLAYER_STATS":
                player_id = query_params.get('player_id', '')
                if player_id not in self.manager.players:
                    success = False
                    error = {"code": "E005", "message": "PLAYER_NOT_REGISTERED"}
                else:
                    data = self._get_player_stats(player_id)
            else:
                success = False
                error = {"code": "E003", "message": f"Unknown query_type: {query_type}"}
        
        except Exception as e:
            logging.error(f"Error processing query {query_type}: {e}")
            success = False
            error = {"code": "E000", "message": str(e)}
        
        # Return LEAGUE_QUERY_RESPONSE
        response = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_QUERY_RESPONSE",
            "sender": "league_manager",
            "timestamp": get_iso_timestamp(),
            "conversation_id": conversation_id,
            "query_type": query_type,
            "success": success
        }
        
        if success:
            response["data"] = data
        else:
            response["error"] = error
        
        return response
    
    def _find_next_match(self, player_id: str) -> Dict:
        """Find the next match for a player."""
        for player_A, player_B, round_id, match_num in self.manager.schedule:
            match_id = f"R{round_id}M{match_num}"
            if match_id not in self.manager.completed_matches:
                if player_A == player_id or player_B == player_id:
                    opponent_id = player_B if player_A == player_id else player_A
                    round_matches = [m for m in self.manager.schedule if m[2] == round_id]
                    match_index = round_matches.index((player_A, player_B, round_id, match_num))
                    referee_endpoint = self.manager.referee_endpoints[match_index % len(self.manager.referee_endpoints)]
                    
                    return {
                        "match_id": match_id,
                        "round_id": round_id,
                        "opponent_id": opponent_id,
                        "referee_endpoint": referee_endpoint
                    }
        return None
    
    def _get_player_stats(self, player_id: str) -> Dict:
        """Get detailed stats for a specific player."""
        standings = calculate_standings(self.manager.results)
        player_stats = next((s for s in standings if s['player_id'] == player_id), None)
        player_info = self.manager.players[player_id]
        
        if player_stats:
            return {
                "player_id": player_id,
                "display_name": player_info['display_name'],
                "stats": player_stats,
                "registered_at": player_info.get('registered_at', '')
            }
        else:
            return {
                "player_id": player_id,
                "display_name": player_info['display_name'],
                "stats": {"played": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0}
            }
