"""League Manager - Orchestrates league operations."""
import asyncio
import argparse
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))

from utils.mcp_server import MCPServer
from utils.mcp_client import MCPClient
from utils.helpers import generate_round_robin_schedule, calculate_standings, get_iso_timestamp, setup_logging
from utils.schemas import PlayerMeta, RegistrationResponse
import uvicorn


class LeagueManager:
    """League Manager MCP Server."""
    
    def __init__(self, config: dict):
        self.config = config
        self.league_id = config['league']['league_id']
        self.registration_timeout = config['league'].get('registration_timeout', 60)
        
        # Player registry
        self.players = {}
        self.player_counter = 0
        self.player_tokens = {}  # {player_id: auth_token}
        
        # Referee registry (NEW for v2)
        self.referees = {}
        self.referee_counter = 0
        self.referee_tokens = {}  # {referee_id: auth_token}
        
        # League state
        self.schedule = []
        self.results = {}
        self.registration_closed = False
        self.completed_matches = set()
        self.expected_matches = 0
        
        # Round tracking
        self.rounds_info = {}  # {round_id: {"matches": [...], "completed": 0}}
        self.completed_rounds = set()
        self.total_rounds = 0
        
        # MCP components
        self.mcp_server = MCPServer("LeagueManager")
        self.mcp_client = MCPClient()
        
        # Referee endpoints from config
        self.referee_endpoints = [
            f"http://{r['host']}:{r['port']}/mcp" 
            for r in config['agents']['referees']
        ]
        self.referee_index = 0
        
        self._setup_tools()
        logging.info(f"League Manager initialized: {self.league_id}")
    
    def _setup_tools(self):
        """Register MCP tools."""
        self.mcp_server.register_tool("register_referee", self.register_referee)  # NEW
        self.mcp_server.register_tool("register_player", self.register_player)
        self.mcp_server.register_tool("report_match_result", self.report_match_result)
        self.mcp_server.register_tool("get_standings", self.get_standings)
        self.mcp_server.register_tool("handle_league_query", self.handle_league_query)  # NEW for V2
    
    def _validate_auth_token(self, sender: str, provided_token: str) -> bool:
        """Validate that provided auth_token matches stored token for sender."""
        if not provided_token:
            return False
        
        # Parse sender format: "player:P01" or "referee:REF01"
        if ":" not in sender:
            return False
        
        agent_type, agent_id = sender.split(":", 1)
        
        if agent_type == "player":
            return self.player_tokens.get(agent_id) == provided_token
        elif agent_type == "referee":
            return self.referee_tokens.get(agent_id) == provided_token
        
        return False
    
    async def register_referee(self, args: dict) -> dict:
        """Handle referee registration (NEW for v2)."""
        from utils.helpers import generate_auth_token
        
        referee_meta = args.get('referee_meta', {})
        
        # Validate required fields
        required = ['display_name', 'version', 'game_types', 'contact_endpoint']
        for field in required:
            if field not in referee_meta:
                return self.mcp_server.create_league_error(
                    "E003", "MISSING_REQUIRED_FIELD",
                    context={"missing_field": field}
                )
        
        # Generate referee ID
        self.referee_counter += 1
        referee_id = f"REF{self.referee_counter:02d}"
        
        # Generate auth token
        auth_token = generate_auth_token("referee", referee_id)
        
        # Store referee info
        self.referees[referee_id] = {
            "referee_id": referee_id,
            "display_name": referee_meta['display_name'],
            "endpoint": referee_meta['contact_endpoint'],
            "game_types": referee_meta['game_types'],
            "max_concurrent": referee_meta.get('max_concurrent_matches', 1),
            "registered_at": get_iso_timestamp()
        }
        self.referee_tokens[referee_id] = auth_token
        
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
        from utils.helpers import generate_auth_token
        
        if self.registration_closed:
            return self.mcp_server.create_league_error(
                "E018", "REGISTRATION_CLOSED",
                context={"registration_timeout": self.registration_timeout}
            )
        
        player_meta = args.get('player_meta', args)
        
        # Validate protocol version (NEW for v2)
        protocol_version = player_meta.get('protocol_version', '1.0.0')
        if not protocol_version.startswith('2.'):
            return self.mcp_server.create_league_error(
                "E018", "PROTOCOL_VERSION_MISMATCH",
                context={
                    "provided_version": protocol_version,
                    "required_version": "2.1.0"
                }
            )
        
        # Validate game type
        game_types = player_meta.get('game_types', [])
        if self.config['league']['game_type'] not in game_types:
            return {
                "message_type": "LEAGUE_REGISTER_RESPONSE",
                "status": "REJECTED",
                "reason": "Game type not supported"
            }
        
        # Generate player ID and auth token
        self.player_counter += 1
        player_id = f"P{self.player_counter:02d}"
        auth_token = generate_auth_token("player", player_id)
        
        # Store player info
        self.players[player_id] = {
            "player_id": player_id,
            "display_name": player_meta.get('display_name', f"Player {player_id}"),
            "endpoint": player_meta['contact_endpoint'],
            "registered_at": get_iso_timestamp()
        }
        self.player_tokens[player_id] = auth_token
        
        logging.info(f"Player registered: {player_id} - {self.players[player_id]['display_name']}")
        
        return {
            "message_type": "LEAGUE_REGISTER_RESPONSE",
            "status": "ACCEPTED",
            "player_id": player_id,
            "auth_token": auth_token,
            "league_id": self.league_id,
            "reason": None
        }
    
    async def report_match_result(self, args: dict) -> dict:
        """Receive match result from referee."""
        # Validate auth_token (NEW for v2)
        sender = args.get('sender', '')
        auth_token = args.get('auth_token', '')
        
        if not self._validate_auth_token(sender, auth_token):
            logging.warning(f"Invalid auth token from {sender}")
            return self.mcp_server.create_league_error(
                "E012", "AUTH_TOKEN_INVALID",
                context={"sender": sender}
            )
        
        # Extract result data from V2 structure
        match_id = args.get('match_id')
        result = args.get('result', {})
        
        self.results[match_id] = {
            "winner": result.get('winner'),
            "score": result.get('score', {}),
            "details": result.get('details', {})
        }
        self.completed_matches.add(match_id)
        logging.info(f"Match result recorded: {match_id} ({len(self.completed_matches)}/{self.expected_matches})")
        self._save_state()
        
        # Check if round is complete
        await self._check_round_completion(match_id)
        
        return {"status": "OK"}
    
    async def get_standings(self, args: dict) -> dict:
        """Calculate and return standings."""
        standings = calculate_standings(self.results)
        return {"standings": standings}
    
    async def handle_league_query(self, args: dict) -> dict:
        """
        Handle LEAGUE_QUERY requests from players or referees.
        Per spec section 4.9 - supports GET_STANDINGS, GET_SCHEDULE, GET_NEXT_MATCH, GET_PLAYER_STATS.
        """
        from utils.helpers import generate_conversation_id
        
        # Validate auth token
        sender = args.get('sender', '')
        auth_token = args.get('auth_token', '')
        
        if not self._validate_auth_token(sender, auth_token):
            return self.mcp_server.create_league_error(
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
                standings = calculate_standings(self.results)
                # Add display names to standings
                for entry in standings:
                    player_info = self.players.get(entry['player_id'], {})
                    entry['display_name'] = player_info.get('display_name', entry['player_id'])
                data = {"standings": standings}
            
            elif query_type == "GET_SCHEDULE":
                # Return full schedule with match details
                schedule_data = []
                for player_A, player_B, round_id, match_num in self.schedule:
                    match_id = f"R{round_id}M{match_num}"
                    schedule_data.append({
                        "match_id": match_id,
                        "round_id": round_id,
                        "player_A_id": player_A,
                        "player_B_id": player_B,
                        "completed": match_id in self.completed_matches
                    })
                data = {"schedule": schedule_data, "total_matches": len(self.schedule)}
            
            elif query_type == "GET_NEXT_MATCH":
                # Find next match for requesting player
                player_id = query_params.get('player_id', '')
                next_match = None
                
                for player_A, player_B, round_id, match_num in self.schedule:
                    match_id = f"R{round_id}M{match_num}"
                    if match_id not in self.completed_matches:
                        if player_A == player_id or player_B == player_id:
                            opponent_id = player_B if player_A == player_id else player_A
                            # Find referee endpoint for this match
                            round_matches = [m for m in self.schedule if m[2] == round_id]
                            match_index = round_matches.index((player_A, player_B, round_id, match_num))
                            referee_endpoint = self.referee_endpoints[match_index % len(self.referee_endpoints)]
                            
                            next_match = {
                                "match_id": match_id,
                                "round_id": round_id,
                                "opponent_id": opponent_id,
                                "referee_endpoint": referee_endpoint
                            }
                            break
                
                if next_match:
                    data = {"next_match": next_match}
                else:
                    data = {"next_match": None, "message": "No upcoming matches"}
            
            elif query_type == "GET_PLAYER_STATS":
                # Get detailed stats for a specific player
                player_id = query_params.get('player_id', '')
                
                if player_id not in self.players:
                    success = False
                    error = {"code": "E005", "message": "PLAYER_NOT_REGISTERED"}
                else:
                    standings = calculate_standings(self.results)
                    player_stats = next((s for s in standings if s['player_id'] == player_id), None)
                    
                    if player_stats:
                        player_info = self.players[player_id]
                        data = {
                            "player_id": player_id,
                            "display_name": player_info['display_name'],
                            "stats": player_stats,
                            "registered_at": player_info.get('registered_at', '')
                        }
                    else:
                        data = {
                            "player_id": player_id,
                            "display_name": self.players[player_id]['display_name'],
                            "stats": {
                                "played": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0
                            }
                        }
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
    
    async def _check_round_completion(self, match_id: str):
        """Check if a round has completed and notify players."""
        # Extract round_id from match_id (e.g., "R1M1" -> 1)
        round_id = int(match_id[1:match_id.index('M')])
        
        if round_id in self.completed_rounds:
            return  # Already processed this round
        
        # Count completed matches in this round
        round_info = self.rounds_info.get(round_id, {})
        if not round_info:
            return
        
        round_info['completed'] += 1
        
        # Check if all matches in this round are complete
        if round_info['completed'] >= len(round_info['matches']):
            self.completed_rounds.add(round_id)
            logging.info(f"Round {round_id} completed!")
            
            # Calculate and notify standings
            standings = calculate_standings(self.results)
            await self._notify_round_standings(round_id, standings)
            
            # Send ROUND_COMPLETED notification
            await self._send_round_completed(round_id, round_info)
    
    async def _notify_round_standings(self, round_id: int, standings: list):
        """Notify all players of current standings after round completion."""
        from utils.helpers import generate_conversation_id
        
        logging.info(f"Notifying all players of Round {round_id} standings")
        
        message = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_STANDINGS_UPDATE",
            "sender": "league_manager",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"standings-r{round_id}"),
            "league_id": self.league_id,
            "round_id": round_id,
            "standings": standings
        }
        
        # Send to all registered players
        for player_id, player_info in self.players.items():
            try:
                await self.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_standings",
                    message
                )
                logging.info(f"Standings sent to {player_id}")
            except Exception as e:
                logging.error(f"Failed to send standings to {player_id}: {e}")
    
    def _save_state(self):
        """Persist league state to disk."""
        Path("data").mkdir(exist_ok=True)
        with open("data/league_state.json", "w") as f:
            json.dump({
                "league_id": self.league_id,
                "players": self.players,
                "results": self.results,
                "schedule": self.schedule
            }, f, indent=2)
    
    async def _announce_round(self, round_id: int, matches_info: list):
        """Send ROUND_ANNOUNCEMENT to all players before round starts."""
        from utils.helpers import generate_conversation_id
        
        logging.info(f"Announcing Round {round_id} with {len(matches_info)} matches")
        
        # Build match announcements
        match_announcements = []
        for match_info in matches_info:
            match_announcements.append({
                "match_id": match_info["match_id"],
                "game_type": "even_odd",
                "player_A_id": match_info["player_A_id"],
                "player_B_id": match_info["player_B_id"],
                "referee_endpoint": match_info["referee_endpoint"]
            })
        
        message = {
            "protocol": "league.v2",
            "message_type": "ROUND_ANNOUNCEMENT",
            "sender": "league_manager",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"round-{round_id}"),
            "league_id": self.league_id,
            "round_id": round_id,
            "matches": match_announcements
        }
        
        # Send to all players
        for player_id, player_info in self.players.items():
            try:
                await self.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_round",
                    message
                )
                logging.info(f"Round announcement sent to {player_id}")
            except Exception as e:
                logging.error(f"Failed to send round announcement to {player_id}: {e}")
    
    async def _send_round_completed(self, round_id: int, round_info: dict):
        """Send ROUND_COMPLETED message to all players."""
        from utils.helpers import generate_conversation_id
        
        logging.info(f"Sending ROUND_COMPLETED for Round {round_id}")
        
        # Calculate next round
        next_round_id = round_id + 1 if round_id < self.total_rounds else None
        
        # Calculate summary
        wins = 0
        draws = 0
        technical_losses = 0
        for match_id in round_info['matches']:
            if match_id in self.results:
                result = self.results[match_id]
                if result['winner'] is None:
                    draws += 1
                else:
                    wins += 1
        
        message = {
            "protocol": "league.v2",
            "message_type": "ROUND_COMPLETED",
            "sender": "league_manager",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"round-{round_id}-complete"),
            "league_id": self.league_id,
            "round_id": round_id,
            "matches_completed": len(round_info['matches']),
            "next_round_id": next_round_id,
            "summary": {
                "total_matches": len(round_info['matches']),
                "wins": wins,
                "draws": draws,
                "technical_losses": technical_losses
            }
        }
        
        # Send to all players
        for player_id, player_info in self.players.items():
            try:
                await self.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_round_completed",
                    message
                )
                logging.info(f"ROUND_COMPLETED sent to {player_id}")
            except Exception as e:
                logging.error(f"Failed to send ROUND_COMPLETED to {player_id}: {e}")
    
    async def _send_league_completed(self, standings: list):
        """Send LEAGUE_COMPLETED message to all agents (players and referees)."""
        from utils.helpers import generate_conversation_id
        
        logging.info("Sending LEAGUE_COMPLETED to all agents")
        
        if not standings:
            logging.warning("No standings available for LEAGUE_COMPLETED")
            return
        
        champion = standings[0]
        
        message = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_COMPLETED",
            "sender": "league_manager",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id("league-complete"),
            "league_id": self.league_id,
            "total_rounds": self.total_rounds,
            "total_matches": self.expected_matches,
            "champion": {
                "player_id": champion['player_id'],
                "display_name": self.players.get(champion['player_id'], {}).get('display_name', 'Unknown'),
                "points": champion['points']
            },
            "final_standings": [
                {"rank": s['rank'], "player_id": s['player_id'], "points": s['points']}
                for s in standings
            ]
        }
        
        # Send to all players
        for player_id, player_info in self.players.items():
            try:
                await self.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_league_completed",
                    message
                )
                logging.info(f"LEAGUE_COMPLETED sent to player {player_id}")
            except Exception as e:
                logging.error(f"Failed to send LEAGUE_COMPLETED to {player_id}: {e}")
        
        # Send to all referees
        for referee_id, referee_info in self.referees.items():
            try:
                await self.mcp_client.call_tool(
                    referee_info['endpoint'],
                    "notify_league_completed",
                    message
                )
                logging.info(f"LEAGUE_COMPLETED sent to referee {referee_id}")
            except Exception as e:
                logging.error(f"Failed to send LEAGUE_COMPLETED to {referee_id}: {e}")
    
    async def run_league(self):
        """Execute full league workflow."""
        logging.info("Waiting for player registration...")
        await asyncio.sleep(self.registration_timeout)
        self.registration_closed = True
        
        player_ids = list(self.players.keys())
        logging.info(f"Registration closed. Players: {player_ids}")
        
        self.schedule = generate_round_robin_schedule(player_ids)
        self.expected_matches = len(self.schedule)
        logging.info(f"Schedule created: {self.expected_matches} matches")
        
        # Build rounds_info for tracking
        for player_A, player_B, round_id, match_num in self.schedule:
            if round_id not in self.rounds_info:
                self.rounds_info[round_id] = {"matches": [], "completed": 0}
                self.total_rounds = max(self.total_rounds, round_id)
            match_id = f"R{round_id}M{match_num}"
            self.rounds_info[round_id]['matches'].append(match_id)
        
        logging.info(f"Total rounds: {self.total_rounds}")
        
        # Group matches by round for round announcements
        rounds_matches = {}
        for player_A, player_B, round_id, match_num in self.schedule:
            if round_id not in rounds_matches:
                rounds_matches[round_id] = []
            
            match_id = f"R{round_id}M{match_num}"
            referee_endpoint = self.referee_endpoints[self.referee_index]
            self.referee_index = (self.referee_index + 1) % len(self.referee_endpoints)
            
            rounds_matches[round_id].append({
                "match_id": match_id,
                "player_A_id": player_A,
                "player_B_id": player_B,
                "player_A_endpoint": self.players[player_A]['endpoint'],
                "player_B_endpoint": self.players[player_B]['endpoint'],
                "referee_endpoint": referee_endpoint,
                "round_id": round_id
            })
        
        # Execute rounds with announcements
        for round_id in sorted(rounds_matches.keys()):
            round_matches = rounds_matches[round_id]
            
            # Send ROUND_ANNOUNCEMENT
            await self._announce_round(round_id, round_matches)
            
            # Start all matches in this round
            for match_info in round_matches:
                await self.mcp_client.call_tool(
                    match_info['referee_endpoint'],
                    "start_match",
                    {
                        "match_id": match_info['match_id'],
                        "round_id": match_info['round_id'],
                        "player_A_id": match_info['player_A_id'],
                        "player_B_id": match_info['player_B_id'],
                        "player_A_endpoint": match_info['player_A_endpoint'],
                        "player_B_endpoint": match_info['player_B_endpoint'],
                        "league_id": self.league_id,
                        "league_manager_endpoint": f"http://{self.config['agents']['league_manager']['host']}:{self.config['agents']['league_manager']['port']}/mcp"
                    }
                )
        
        # Wait for all matches to complete
        logging.info("Waiting for all matches to complete...")
        while len(self.completed_matches) < self.expected_matches:
            await asyncio.sleep(1)
        
        logging.info("All matches completed!")
        
        # Calculate final standings
        standings = calculate_standings(self.results)
        
        # Send LEAGUE_COMPLETED to all agents
        await self._send_league_completed(standings)
        
        # Display comprehensive results
        print("\n" + "="*60)
        print("  LEAGUE COMPLETE - FINAL RESULTS")
        print("="*60)
        print(f"\nLeague: {self.league_id}")
        print(f"Total Matches Played: {self.expected_matches}")
        print(f"Total Players: {len(player_ids)}\n")
        
        print("-"*60)
        print("FINAL STANDINGS")
        print("-"*60)
        print(f"{'Rank':<6} {'Player':<12} {'Played':<8} {'W':<4} {'D':<4} {'L':<4} {'Points':<8}")
        print("-"*60)
        
        for entry in standings:
            print(f"{entry['rank']:<6} {entry['player_id']:<12} "
                  f"{entry['played']:<8} {entry['wins']:<4} {entry['draws']:<4} "
                  f"{entry['losses']:<4} {entry['points']:<8}")
        
        # Announce the winner
        if standings:
            winner = standings[0]
            print("\n" + "="*60)
            print("  🏆 WINNER ANNOUNCEMENT 🏆")
            print("="*60)
            print(f"\nCongratulations to {winner['player_id']} - {self.players.get(winner['player_id'], {}).get('display_name', 'Unknown')}!")
            print(f"Final Score: {winner['points']} points ({winner['wins']} wins, {winner['draws']} draws, {winner['losses']} losses)")
            print("\n" + "="*60 + "\n")
        
        logging.info(f"Winner: {winner['player_id']} with {winner['points']} points")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/local_config.yaml")
    args = parser.parse_args()
    
    with open(args.config) as f:
        config = yaml.safe_load(f)
    
    # Setup logging with file output
    log_config = config.get('logging', {})
    setup_logging(
        log_dir=log_config.get('directory', 'logs'),
        log_file='league_manager.log',
        level=log_config.get('level', 'INFO')
    )
    
    manager = LeagueManager(config)
    
    # Create a config for uvicorn
    uvicorn_config = uvicorn.Config(
        manager.mcp_server.app,
        host=config['agents']['league_manager']['host'],
        port=config['agents']['league_manager']['port'],
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    
    # Run both server and league manager concurrently
    await asyncio.gather(
        server.serve(),
        manager.run_league()
    )


if __name__ == "__main__":
    asyncio.run(main())
