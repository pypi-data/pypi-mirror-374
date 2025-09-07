"""
MCP Utility Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP

from .shared_utils import get_yahoo_query, handle_api_error
from .enhancement_helpers import DataEnhancer

logger = logging.getLogger(__name__)


def register_utility_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register all MCP utility tools."""


    @mcp.tool()
    def get_all_yahoo_fantasy_game_keys() -> Dict[str, Any]:
        """
        Get all available Yahoo Fantasy game keys across all sports.

        Returns:
            All available game keys
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = "all_yahoo_fantasy_game_keys"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, None, "nfl")  # Use NFL as default
            game_keys = yahoo_query.get_all_yahoo_fantasy_game_keys()

            keys_data = []
            if game_keys:
                for key in game_keys:
                    keys_data.append(str(key))

            result = {
                "total_game_keys": len(keys_data),
                "game_keys": keys_data
            }

            # Cache permanently since game keys don't change often
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            return handle_api_error("getting all Yahoo fantasy game keys", e)

    @mcp.tool()
    def get_current_game_info(sport: str = "nfl") -> Dict[str, Any]:
        """
        Get current game information for a specific sport.

        Args:
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Current game information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"current_game_info/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, None, sport)
            game_info = yahoo_query.get_current_game_info()

            result = {
                "sport": sport,
                "game_key": str(getattr(game_info, 'game_key', 'Unknown')),
                "game_id": str(getattr(game_info, 'game_id', 'Unknown')),
                "name": str(getattr(game_info, 'name', 'Unknown')),
                "code": str(getattr(game_info, 'code', sport)),
                "type": str(getattr(game_info, 'type', 'Unknown')),
                "url": str(getattr(game_info, 'url', 'Unknown')),
                "season": str(getattr(game_info, 'season', 'Unknown')),
                "is_registration_over": getattr(game_info, 'is_registration_over', False),
                "is_game_over": getattr(game_info, 'is_game_over', False),
                "is_offseason": getattr(game_info, 'is_offseason', False)
            }

            # Cache for 1 hour since current game info can change
            cache_manager.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            return handle_api_error("getting current game info", e)

    @mcp.tool()
    def get_current_game_metadata(sport: str = "nfl") -> Dict[str, Any]:
        """
        Get current game metadata for a specific sport.

        Args:
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Current game metadata information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"current_game_metadata/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, None, sport)
            metadata = yahoo_query.get_current_game_metadata()

            result = {
                "sport": sport,
                "game_key": str(getattr(metadata, 'game_key', 'Unknown')),
                "game_id": str(getattr(metadata, 'game_id', 'Unknown')),
                "name": str(getattr(metadata, 'name', 'Unknown')),
                "code": str(getattr(metadata, 'code', sport)),
                "type": str(getattr(metadata, 'type', 'Unknown')),
                "url": str(getattr(metadata, 'url', 'Unknown')),
                "season": str(getattr(metadata, 'season', 'Unknown')),
                "is_registration_over": getattr(metadata, 'is_registration_over', False),
                "is_game_over": getattr(metadata, 'is_game_over', False),
                "is_offseason": getattr(metadata, 'is_offseason', False)
            }

            # Cache for 1 hour since current game metadata can change
            cache_manager.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            return handle_api_error("getting current game metadata", e)

    @mcp.tool()
    def get_current_user() -> Dict[str, Any]:
        """
        Get information about the currently authenticated user.

        Returns:
            Current user information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = "current_user"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, None, "nfl")  # Use NFL as default
            user = yahoo_query.get_current_user()

            result = {
                "user_guid": str(getattr(user, 'user_guid', 'Unknown')),
                "user_key": str(getattr(user, 'user_key', 'Unknown')),
                "profile": getattr(user, 'profile', {})
            }

            # Cache for 1 hour since user info doesn't change often
            cache_manager.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            return handle_api_error("getting current user", e)

    @mcp.tool()
    def get_response(league_id: str, resource_path: str, sport: str = "nfl",
                     season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get raw response from Yahoo API for a custom resource path.

        Args:
            league_id: Yahoo league ID
            resource_path: Custom Yahoo API resource path
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Raw API response
        """
        try:
            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            response = yahoo_query.get_response(resource_path)

            result = {
                "league_id": league_id,
                "resource_path": resource_path,
                "sport": sport,
                "season": season or "current",
                "response": response
            }

            return result

        except Exception as e:
            return handle_api_error("getting custom response", e)

    @mcp.tool()
    def get_user_games(sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all games the authenticated user has access to for a specific sport.

        Args:
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            User's games information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"user_games/{sport}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)  # League ID not needed for user games
            user_games = yahoo_query.get_user_games()

            games_data = []
            if user_games:
                for game in user_games:
                    game_data = {
                        "game_key": str(getattr(game, 'game_key', 'Unknown')),
                        "game_id": str(getattr(game, 'game_id', 'Unknown')),
                        "name": str(getattr(game, 'name', 'Unknown')),
                        "code": str(getattr(game, 'code', 'Unknown')),
                        "type": str(getattr(game, 'type', 'Unknown')),
                        "url": str(getattr(game, 'url', 'Unknown')),
                        "season": str(getattr(game, 'season', 'Unknown')),
                        "is_registration_over": getattr(game, 'is_registration_over', False),
                        "is_game_over": getattr(game, 'is_game_over', False),
                        "is_offseason": getattr(game, 'is_offseason', False)
                    }
                    games_data.append(game_data)

            result = {
                "sport": sport,
                "season": season or "current",
                "total_games": len(games_data),
                "games": games_data
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            return handle_api_error("getting user games", e)

    @mcp.tool()
    def get_user_teams(sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all teams the authenticated user owns across all leagues for a specific sport.

        Args:
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            User's teams information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"user_teams/{sport}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)  # League ID not needed for user teams
            user_teams = yahoo_query.get_user_teams()

            # Use DataEnhancer for proper data extraction
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            teams_data = []
            if user_teams:
                for team in user_teams:
                    # Extract team name properly using DataEnhancer techniques
                    team_name = data_enhancer._decode_name_bytes(getattr(team, 'name', 'Unknown'))
                    
                    team_data = {
                        "team_key": str(getattr(team, 'team_key', 'Unknown')),
                        "team_id": str(getattr(team, 'team_id', 'Unknown')),
                        "name": team_name,
                        "is_owned_by_current_login": getattr(team, 'is_owned_by_current_login', False),
                        "url": str(getattr(team, 'url', 'Unknown')),
                        "team_logos": getattr(team, 'team_logos', []),
                        "waiver_priority": getattr(team, 'waiver_priority', 0),
                        "number_of_moves": getattr(team, 'number_of_moves', 0),
                        "number_of_trades": getattr(team, 'number_of_trades', 0),
                        "roster_adds": getattr(team, 'roster_adds', {}),
                        "league_scoring_type": str(getattr(team, 'league_scoring_type', 'Unknown')),
                        "has_draft_grade": getattr(team, 'has_draft_grade', False),
                        "managers": []
                    }

                    # Add manager information if available
                    if hasattr(team, 'managers') and team.managers:
                        for manager in team.managers:
                            manager_data = {
                                "manager_id": str(getattr(manager, 'manager_id', 'Unknown')),
                                "nickname": str(getattr(manager, 'nickname', 'Unknown')),
                                "guid": str(getattr(manager, 'guid', 'Unknown')),
                                "is_commissioner": getattr(manager, 'is_commissioner', False),
                                "is_current_login": getattr(manager, 'is_current_login', False),
                                "email": str(getattr(manager, 'email', 'Unknown')),
                                "image_url": str(getattr(manager, 'image_url', 'Unknown'))
                            }
                            managers_list = team_data.get("managers")
                            if isinstance(managers_list, list):
                                managers_list.append(manager_data)

                    teams_data.append(team_data)

            result = {
                "sport": sport,
                "season": season or "current",
                "total_teams": len(teams_data),
                "teams": teams_data
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            return handle_api_error("getting user teams", e)
