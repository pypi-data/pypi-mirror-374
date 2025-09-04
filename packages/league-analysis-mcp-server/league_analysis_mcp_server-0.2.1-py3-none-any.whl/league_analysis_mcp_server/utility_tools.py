"""
MCP Utility Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_utility_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register all MCP utility tools."""

    def get_yahoo_query(league_id: str, game_id: Optional[str] = None, sport: str = "nfl") -> YahooFantasySportsQuery:
        """Create a Yahoo Fantasy Sports Query object."""
        auth_manager = app_state["auth_manager"]

        if not auth_manager.is_configured():
            raise ValueError("Yahoo authentication not configured. Run check_setup_status() to begin setup.")

        auth_credentials = auth_manager.get_auth_credentials()

        # Use game_id if provided, otherwise use current season
        if game_id:
            query_params = {**auth_credentials, 'game_id': game_id}
        else:
            query_params = {**auth_credentials, 'game_code': sport}

        return YahooFantasySportsQuery(
            league_id=league_id,
            **query_params
        )

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

            yahoo_query = get_yahoo_query("temp", None, "nfl")  # Use NFL as default
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
            logger.error(f"Error getting all Yahoo fantasy game keys: {e}")
            return {"error": str(e)}

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

            yahoo_query = get_yahoo_query("temp", None, sport)
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
            logger.error(f"Error getting current game info: {e}")
            return {"error": str(e)}

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

            yahoo_query = get_yahoo_query("temp", None, sport)
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
            logger.error(f"Error getting current game metadata: {e}")
            return {"error": str(e)}

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

            yahoo_query = get_yahoo_query("temp", None, "nfl")  # Use NFL as default
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
            logger.error(f"Error getting current user: {e}")
            return {"error": str(e)}

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

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
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
            logger.error(f"Error getting custom response: {e}")
            return {"error": str(e)}
