"""
Enhancement Helper Functions for YFPY Data Structures

This module provides standardized enhancement functions to make YFPY data
readable and actionable across all tools.
"""

import logging
from typing import Dict, Any, List, Union, Optional
from yfpy import YahooFantasySportsQuery

logger = logging.getLogger(__name__)


class DataEnhancer:
    """Centralized data enhancement for all YFPY methods."""

    def __init__(self, yahoo_query: YahooFantasySportsQuery, cache_manager=None):
        self.yahoo_query = yahoo_query
        self.cache_manager = cache_manager
        self._team_names_cache: Optional[Dict[str, str]] = None
        self._player_cache: Dict[str, Dict[str, Any]] = {}

    def get_team_names(self) -> Dict[str, str]:
        """Get team key to team name mapping."""
        if self._team_names_cache is None:
            try:
                standings = self.yahoo_query.get_league_standings()
                team_names = {}
                for team in standings.teams:
                    team_key = getattr(team, 'team_key', '')
                    team_name = getattr(team, 'name', 'Unknown Team')
                    if isinstance(team_name, bytes):
                        team_name = team_name.decode('utf-8')
                    team_names[team_key] = team_name
                self._team_names_cache = team_names
            except Exception as e:
                logger.warning(f"Failed to get team names: {e}")
                self._team_names_cache = {}
        return self._team_names_cache

    def get_player_info(self, player_key: str) -> Dict[str, Any]:
        """Get enhanced player information from player key."""
        if player_key in self._player_cache:
            return self._player_cache[player_key]

        try:
            player_stats = self.yahoo_query.get_player_stats_for_season(player_key)
            if player_stats and hasattr(player_stats, 'name'):
                player_info = {
                    "player_name": player_stats.name.full if player_stats.name.full else 'Unknown Player',
                    "player_position": getattr(player_stats, 'display_position', 'Unknown'),
                    "player_team": getattr(player_stats, 'editorial_team_abbr', 'Unknown'),
                    "player_id": getattr(player_stats, 'player_id', 'Unknown')
                }
            else:
                player_info = {
                    "player_name": f'Player {player_key}',
                    "player_position": 'Unknown',
                    "player_team": 'Unknown',
                    "player_id": 'Unknown'
                }
        except Exception as e:
            logger.warning(f"Failed to get player info for {player_key}: {e}")
            player_info = {
                "player_name": f'Player {player_key}',
                "player_position": 'Unknown',
                "player_team": 'Unknown',
                "player_id": 'Unknown'
            }

        self._player_cache[player_key] = player_info
        return player_info

    def enhance_draft_pick(self, pick) -> Dict[str, Any]:
        """Enhance a single draft pick with readable information."""
        team_names = self.get_team_names()

        pick_data = {
            "pick": getattr(pick, 'pick', 0),
            "round": getattr(pick, 'round', 0),
            "team_key": str(getattr(pick, 'team_key', 'Unknown')),
            "team_name": team_names.get(getattr(pick, 'team_key', ''), 'Unknown Team'),
            "player_key": str(getattr(pick, 'player_key', 'Unknown')),
            "cost": getattr(pick, 'cost', 0)
        }

        # Add player information
        player_info = self.get_player_info(pick.player_key)
        pick_data.update(player_info)

        return pick_data

    def enhance_team_data(self, team) -> Dict[str, Any]:
        """Enhance team data with readable information."""
        team_data: Dict[str, Any] = {
            "team_id": getattr(team, 'team_id', 'Unknown'),
            "team_key": str(getattr(team, 'team_key', 'Unknown')),
            "name": self._decode_bytes(getattr(team, 'name', 'Unknown Team')),
            "wins": getattr(team, 'wins', 0),
            "losses": getattr(team, 'losses', 0),
            "ties": getattr(team, 'ties', 0),
            "points_for": getattr(team, 'points_for', 0.0),
            "points_against": getattr(team, 'points_against', 0.0),
            "waiver_priority": getattr(team, 'waiver_priority', 0),
            "number_of_moves": getattr(team, 'number_of_moves', 0),
            "number_of_trades": getattr(team, 'number_of_trades', 0),
            "managers": []
        }

        # Add manager information
        if hasattr(team, 'managers') and team.managers:
            for manager in team.managers:
                manager_data = {
                    "manager_id": str(getattr(manager, 'manager_id', 'Unknown')),
                    "nickname": self._decode_bytes(getattr(manager, 'nickname', 'Unknown')),
                    "guid": str(getattr(manager, 'guid', 'Unknown')),
                    "is_commissioner": getattr(manager, 'is_commissioner', False),
                    "is_current_login": getattr(manager, 'is_current_login', False),
                    "email": str(getattr(manager, 'email', 'Unknown')),
                    "image_url": str(getattr(manager, 'image_url', 'Unknown'))
                }
                managers_list = team_data.get("managers")
                if isinstance(managers_list, list):
                    managers_list.append(manager_data)

        return team_data

    def enhance_transaction(self, transaction) -> Dict[str, Any]:
        """Enhance transaction data with readable information."""
        team_names = self.get_team_names()

        transaction_data: Dict[str, Any] = {
            "transaction_id": getattr(transaction, 'transaction_id', 0),
            "transaction_key": str(getattr(transaction, 'transaction_key', 'Unknown')),
            "type": str(getattr(transaction, 'type', 'Unknown')),
            "status": str(getattr(transaction, 'status', 'Unknown')),
            "timestamp": getattr(transaction, 'timestamp', 0),
            "faab_bid": getattr(transaction, 'faab_bid', None),
            "trader_team_key": str(getattr(transaction, 'trader_team_key', '')),
            "trader_team_name": team_names.get(getattr(transaction, 'trader_team_key', ''), 'Unknown'),
            "tradee_team_key": str(getattr(transaction, 'tradee_team_key', '')),
            "tradee_team_name": team_names.get(getattr(transaction, 'tradee_team_key', ''), 'Unknown'),
            "players": []
        }

        # Add player information if available
        if hasattr(transaction, 'players') and transaction.players:
            for player in transaction.players:
                player_key = getattr(player, 'player_key', '')
                if player_key:
                    player_info = self.get_player_info(player_key)
                    players_list = transaction_data.get("players")
                    if isinstance(players_list, list):
                        players_list.append({
                            "player_key": player_key,
                            **player_info,
                            "transaction_data": getattr(player, 'transaction_data', {})
                        })

        return transaction_data

    def enhance_roster_player(self, player) -> Dict[str, Any]:
        """Enhance roster player data."""
        player_data = {
            "player_key": str(getattr(player, 'player_key', 'Unknown')),
            "player_id": str(getattr(player, 'player_id', 'Unknown')),
            "selected_position": str(getattr(player, 'selected_position', 'Unknown')),
            "is_starter": bool(getattr(player, 'is_starter', False)),
            "is_editable": bool(getattr(player, 'is_editable', True))
        }

        # Add enhanced player information
        player_key = player_data["player_key"]
        if player_key and player_key != 'Unknown':
            player_info = self.get_player_info(str(player_key))
            player_data.update(player_info)
        else:
            # Fallback to basic name extraction if available
            if hasattr(player, 'name'):
                name = player.name
                if hasattr(name, 'full'):
                    player_data["player_name"] = name.full
                elif isinstance(name, str):
                    player_data["player_name"] = name
                else:
                    player_data["player_name"] = str(name)
            else:
                player_data["player_name"] = 'Unknown Player'

            player_data["player_position"] = getattr(player, 'display_position', 'Unknown')
            player_data["player_team"] = getattr(player, 'editorial_team_abbr', 'Unknown')

        return player_data

    def _decode_bytes(self, value: Union[str, bytes, Any]) -> str:
        """Helper to decode bytes values to strings."""
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return str(value) if value else 'Unknown'

    def enhance_data_batch(self, data_list: List[Any], enhancement_type: str) -> List[Dict[str, Any]]:
        """Enhance a batch of data objects based on type."""
        enhanced_data = []

        for item in data_list:
            try:
                if enhancement_type == 'draft_pick':
                    enhanced_item = self.enhance_draft_pick(item)
                elif enhancement_type == 'team':
                    enhanced_item = self.enhance_team_data(item)
                elif enhancement_type == 'transaction':
                    enhanced_item = self.enhance_transaction(item)
                elif enhancement_type == 'roster_player':
                    enhanced_item = self.enhance_roster_player(item)
                else:
                    # Generic enhancement - just clean up common issues
                    enhanced_item = self._generic_enhance(item)

                enhanced_data.append(enhanced_item)

            except Exception as e:
                logger.warning(f"Failed to enhance {enhancement_type} item: {e}")
                # Fallback to basic data
                enhanced_data.append({"error": f"Enhancement failed: {e}", "raw_item": str(item)})

        return enhanced_data

    def enhance_league_info(self, league_info) -> Dict[str, Any]:
        """Enhance league info data with readable information."""
        return {
            "league_id": getattr(league_info, 'league_id', 'Unknown'),
            "league_key": str(getattr(league_info, 'league_key', 'Unknown')),
            "name": self._decode_bytes(getattr(league_info, 'name', 'Unknown')),
            "url": str(getattr(league_info, 'url', 'Unknown')),
            "logo_url": str(getattr(league_info, 'logo_url', 'Unknown')),
            "draft_status": str(getattr(league_info, 'draft_status', 'Unknown')),
            "num_teams": getattr(league_info, 'num_teams', 0),
            "edit_key": getattr(league_info, 'edit_key', 0),
            "weekly_deadline": str(getattr(league_info, 'weekly_deadline', 'Unknown')),
            "league_update_timestamp": getattr(league_info, 'league_update_timestamp', 0),
            "scoring_type": str(getattr(league_info, 'scoring_type', 'Unknown')),
            "league_type": str(getattr(league_info, 'league_type', 'Unknown')),
            "renew": str(getattr(league_info, 'renew', 'Unknown')),
            "renewed": str(getattr(league_info, 'renewed', 'Unknown')),
            "iris_group_chat_id": str(getattr(league_info, 'iris_group_chat_id', 'Unknown')),
            "current_week": getattr(league_info, 'current_week', 0),
            "start_week": getattr(league_info, 'start_week', 0),
            "start_date": str(getattr(league_info, 'start_date', 'Unknown')),
            "end_week": getattr(league_info, 'end_week', 0),
            "end_date": str(getattr(league_info, 'end_date', 'Unknown')),
            "game_code": str(getattr(league_info, 'game_code', 'Unknown')),
            "season": str(getattr(league_info, 'season', 'Unknown'))
        }

    def enhance_player_stats(self, player_stats) -> Dict[str, Any]:
        """Enhance player stats data with readable information."""
        enhanced_data = {
            "player_key": str(getattr(player_stats, 'player_key', 'Unknown')),
            "player_id": str(getattr(player_stats, 'player_id', 'Unknown')),
            "editorial_player_key": str(getattr(player_stats, 'editorial_player_key', 'Unknown')),
            "editorial_team_key": str(getattr(player_stats, 'editorial_team_key', 'Unknown')),
            "editorial_team_abbr": str(getattr(player_stats, 'editorial_team_abbr', 'Unknown')),
            "display_position": str(getattr(player_stats, 'display_position', 'Unknown')),
            "headshot": str(getattr(player_stats, 'headshot', 'Unknown')),
            "image_url": str(getattr(player_stats, 'image_url', 'Unknown')),
            "is_undroppable": getattr(player_stats, 'is_undroppable', False),
            "position_type": str(getattr(player_stats, 'position_type', 'Unknown')),
            "primary_position": str(getattr(player_stats, 'primary_position', 'Unknown')),
            "uniform_number": getattr(player_stats, 'uniform_number', 0),
            "player_stats": getattr(player_stats, 'player_stats', {}),
            "player_points": getattr(player_stats, 'player_points', {})
        }

        # Add enhanced name information
        if hasattr(player_stats, 'name') and player_stats.name:
            name = player_stats.name
            enhanced_data.update({
                "player_name": name.full if hasattr(name, 'full') else str(name),
                "first_name": getattr(name, 'first', 'Unknown'),
                "last_name": getattr(name, 'last', 'Unknown'),
                "ascii_first": getattr(name, 'ascii_first', 'Unknown'),
                "ascii_last": getattr(name, 'ascii_last', 'Unknown')
            })
        else:
            enhanced_data.update({
                "player_name": f'Player {enhanced_data["player_key"]}',
                "first_name": 'Unknown',
                "last_name": 'Unknown',
                "ascii_first": 'Unknown',
                "ascii_last": 'Unknown'
            })

        # Resolve team key to team name if possible
        team_names = self.get_team_names()
        team_key = enhanced_data.get("editorial_team_key", "")
        if isinstance(team_key, str) and team_key in team_names:
            enhanced_data["editorial_team_name"] = team_names[team_key]
        else:
            enhanced_data["editorial_team_name"] = enhanced_data.get("editorial_team_abbr", "Unknown")

        return enhanced_data

    def enhance_team_info(self, team_info) -> Dict[str, Any]:
        """Enhance team info data with readable information."""
        enhanced_data = {
            "team_id": getattr(team_info, 'team_id', 'Unknown'),
            "team_key": str(getattr(team_info, 'team_key', 'Unknown')),
            "name": self._decode_bytes(getattr(team_info, 'name', 'Unknown')),
            "is_owned_by_current_login": getattr(team_info, 'is_owned_by_current_login', False),
            "url": str(getattr(team_info, 'url', 'Unknown')),
            "team_logos": getattr(team_info, 'team_logos', []),
            "waiver_priority": getattr(team_info, 'waiver_priority', 0),
            "number_of_moves": getattr(team_info, 'number_of_moves', 0),
            "number_of_trades": getattr(team_info, 'number_of_trades', 0),
            "roster_adds": getattr(team_info, 'roster_adds', {}),
            "league_scoring_type": str(getattr(team_info, 'league_scoring_type', 'Unknown')),
            "has_draft_grade": getattr(team_info, 'has_draft_grade', False),
            "managers": []
        }

        # Add manager information
        if hasattr(team_info, 'managers') and team_info.managers:
            for manager in team_info.managers:
                manager_data = {
                    "manager_id": str(getattr(manager, 'manager_id', 'Unknown')),
                    "nickname": self._decode_bytes(getattr(manager, 'nickname', 'Unknown')),
                    "guid": str(getattr(manager, 'guid', 'Unknown')),
                    "is_commissioner": getattr(manager, 'is_commissioner', False),
                    "is_current_login": getattr(manager, 'is_current_login', False),
                    "email": str(getattr(manager, 'email', 'Unknown')),
                    "image_url": str(getattr(manager, 'image_url', 'Unknown'))
                }
                managers_list = enhanced_data.get("managers")
                if isinstance(managers_list, list):
                    managers_list.append(manager_data)

        return enhanced_data

    def enhance_game_info(self, game_info) -> Dict[str, Any]:
        """Enhance game info data with readable information."""
        return {
            "game_key": str(getattr(game_info, 'game_key', 'Unknown')),
            "game_id": str(getattr(game_info, 'game_id', 'Unknown')),
            "name": str(getattr(game_info, 'name', 'Unknown')),
            "code": str(getattr(game_info, 'code', 'Unknown')),
            "type": str(getattr(game_info, 'type', 'Unknown')),
            "url": str(getattr(game_info, 'url', 'Unknown')),
            "season": str(getattr(game_info, 'season', 'Unknown')),
            "is_registration_over": getattr(game_info, 'is_registration_over', False),
            "is_game_over": getattr(game_info, 'is_game_over', False),
            "is_offseason": getattr(game_info, 'is_offseason', False)
        }

    def _generic_enhance(self, item) -> Dict[str, Any]:
        """Generic enhancement for unknown item types."""
        enhanced = {}

        for attr in dir(item):
            if not attr.startswith('_'):
                try:
                    value = getattr(item, attr)
                    if not callable(value):
                        enhanced[attr] = self._decode_bytes(value)
                except (AttributeError, TypeError):
                    pass

        return enhanced
