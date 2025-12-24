"""League Manager - Scheduling and round management logic."""
import asyncio
import logging
from typing import List, Dict
from league_sdk.helpers import (
    generate_round_robin_schedule,
    generate_conversation_id,
    get_iso_timestamp,
    calculate_standings,
)


class LeagueScheduler:
    """Handles scheduling, round announcements, and league progression."""
    
    def __init__(self, manager):
        """Initialize scheduler with reference to manager."""
        self.manager = manager
    
    def generate_schedule(self, player_ids: List[str]) -> None:
        """Generate round-robin schedule for all players."""
        self.manager.schedule = generate_round_robin_schedule(player_ids)
        self.manager.expected_matches = len(self.manager.schedule)
        
        #Build rounds_info for tracking
        for player_A, player_B, round_id, match_num in self.manager.schedule:
            if round_id not in self.manager.rounds_info:
                self.manager.rounds_info[round_id] = {"matches": [], "completed": 0}
                self.manager.total_rounds = max(self.manager.total_rounds, round_id)
            match_id = f"R{round_id}M{match_num}"
            self.manager.rounds_info[round_id]['matches'].append(match_id)
        
        logging.info(f"Schedule created: {self.manager.expected_matches} matches across {self.manager.total_rounds} rounds")
    
    async def announce_round(self, round_id: int, matches_info: List[Dict]) -> None:
        """Send ROUND_ANNOUNCEMENT to all players before round starts."""
        logging.info(f"Announcing Round {round_id} with {len(matches_info)} matches")
        
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
            "league_id": self.manager.league_id,
            "round_id": round_id,
            "matches": match_announcements
        }
        
        # Send to all players
        for player_id, player_info in self.manager.players.items():
            try:
                await self.manager.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_round",
                    message
                )
                logging.info(f"Round announcement sent to {player_id}")
            except Exception as e:
                logging.error(f"Failed to send round announcement to {player_id}: {e}")
    
    async def check_round_completion(self, match_id: str) -> None:
        """Check if a round has completed and notify players."""
        # Extract round_id from match_id (e.g., "R1M1" -> 1)
        round_id = int(match_id[1:match_id.index('M')])
        
        if round_id in self.manager.completed_rounds:
            return  # Already processed
        
        # Count completed matches in this round
        round_info = self.manager.rounds_info.get(round_id, {})
        if not round_info:
            return
        
        round_info['completed'] = int(round_info.get('completed', 0)) + 1
        
        # Check if all matches complete
        if round_info['completed'] >= len(round_info['matches']):
            self.manager.completed_rounds.add(round_id)
            logging.info(f"Round {round_id} completed!")
            
            # Calculate and notify standings
            standings = calculate_standings(self.manager.results)
            await self.notify_round_standings(round_id, standings)
            await self.send_round_completed(round_id, round_info)
    
    async def notify_round_standings(self, round_id: int, standings: List[Dict]) -> None:
        """Notify all players of current standings after round completion."""
        logging.info(f"Notifying all players of Round {round_id} standings")
        
        message = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_STANDINGS_UPDATE",
            "sender": "league_manager",
            "timestamp": get_iso_timestamp(),
            "conversation_id": generate_conversation_id(f"standings-r{round_id}"),
            "league_id": self.manager.league_id,
            "round_id": round_id,
            "standings": standings
        }
        
        for player_id, player_info in self.manager.players.items():
            try:
                await self.manager.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_standings",
                    message
                )
            except Exception as e:
                logging.error(f"Failed to send standings to {player_id}: {e}")
    
    async def send_round_completed(self, round_id: int, round_info: Dict) -> None:
        """Send ROUND_COMPLETED message to all players."""
        logging.info(f"Sending ROUND_COMPLETED for Round {round_id}")
        
        next_round_id = round_id + 1 if round_id < self.manager.total_rounds else None
        
        # Calculate summary
        wins, draws, technical_losses = 0, 0, 0
        for match_id in round_info['matches']:
            if match_id in self.manager.results:
                result = self.manager.results[match_id]
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
            "league_id": self.manager.league_id,
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
        
        for player_id, player_info in self.manager.players.items():
            try:
                await self.manager.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_round_completed",
                    message
                )
            except Exception as e:
                logging.error(f"Failed to send ROUND_COMPLETED to {player_id}: {e}")
    
    async def send_league_completed(self, standings: List[Dict]) -> None:
        """Send LEAGUE_COMPLETED message to all agents."""
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
            "league_id": self.manager.league_id,
            "total_rounds": self.manager.total_rounds,
            "total_matches": self.manager.expected_matches,
            "champion": {
                "player_id": champion['player_id'],
                "display_name": self.manager.players.get(champion['player_id'], {}).get('display_name', 'Unknown'),
                "points": champion['points']
            },
            "final_standings": [
                {"rank": s['rank'], "player_id": s['player_id'], "points": s['points']}
                for s in standings
            ]
        }
        
        # Send to all players and referees
        for player_id, player_info in self.manager.players.items():
            try:
                await self.manager.mcp_client.call_tool(
                    player_info['endpoint'],
                    "notify_league_completed",
                    message
                )
            except Exception as e:
                logging.error(f"Failed to send LEAGUE_COMPLETED to {player_id}: {e}")
        
        for referee_id, referee_info in self.manager.referees.items():
            try:
                await self.manager.mcp_client.call_tool(
                    referee_info['endpoint'],
                    "notify_league_completed",
                    message
                )
            except Exception as e:
                logging.error(f"Failed to send LEAGUE_COMPLETED to {referee_id}: {e}")
