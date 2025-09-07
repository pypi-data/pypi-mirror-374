"""
MCP Game Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP
from .shared_utils import get_yahoo_query, handle_api_error

logger = logging.getLogger(__name__)


def register_game_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register all MCP game tools."""


    @mcp.tool()
    def get_game_info_by_game_id(game_id: str, sport: str = "nfl") -> Dict[str, Any]:
        """
        Get game information by game ID.

        Args:
            game_id: Yahoo game ID
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Game information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"game_info/{game_id}/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)  # League ID not needed for game info
            game_info = yahoo_query.get_game_info_by_game_id(int(game_id))

            result = {
                "game_id": str(getattr(game_info, 'game_id', game_id)),
                "sport": sport,
                "game_key": str(getattr(game_info, 'game_key', 'Unknown')),
                "name": str(getattr(game_info, 'name', 'Unknown')),
                "code": str(getattr(game_info, 'code', sport)),
                "type": str(getattr(game_info, 'type', 'Unknown')),
                "url": str(getattr(game_info, 'url', 'Unknown')),
                "season": str(getattr(game_info, 'season', 'Unknown')),
                "is_registration_over": getattr(game_info, 'is_registration_over', False),
                "is_game_over": getattr(game_info, 'is_game_over', False),
                "is_offseason": getattr(game_info, 'is_offseason', False)
            }

            # Cache permanently since game info doesn't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game info by game ID: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_game_key_by_season(sport: str, season: str) -> Dict[str, Any]:
        """
        Get game key for a specific sport and season.

        Args:
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Season year (e.g., "2023")

        Returns:
            Game key information
        """
        try:
            # Check if we have this in our game_ids mapping
            game_id = app_state["game_ids"].get(sport, {}).get(season)
            if game_id:
                return {
                    "sport": sport,
                    "season": season,
                    "game_id": game_id,
                    "game_key": f"{game_id}.l.{season}"  # Standard Yahoo game key format
                }

            # If not in our mapping, try to get it from the API
            cache_manager = app_state["cache_manager"]
            cache_key = f"game_key/{sport}/{season}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, None, sport)
            game_key = yahoo_query.get_game_key_by_season(int(season))

            result = {
                "sport": sport,
                "season": season,
                "game_key": str(game_key)
            }

            # Cache permanently since game keys don't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game key by season: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_game_metadata_by_game_id(game_id: str, sport: str = "nfl") -> Dict[str, Any]:
        """
        Get game metadata by game ID.

        Args:
            game_id: Yahoo game ID
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Game metadata information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"game_metadata/{game_id}/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)
            metadata = yahoo_query.get_game_metadata_by_game_id(int(game_id))

            result = {
                "game_id": str(getattr(metadata, 'game_id', game_id)),
                "sport": sport,
                "game_key": str(getattr(metadata, 'game_key', 'Unknown')),
                "name": str(getattr(metadata, 'name', 'Unknown')),
                "code": str(getattr(metadata, 'code', sport)),
                "type": str(getattr(metadata, 'type', 'Unknown')),
                "url": str(getattr(metadata, 'url', 'Unknown')),
                "season": str(getattr(metadata, 'season', 'Unknown')),
                "is_registration_over": getattr(metadata, 'is_registration_over', False),
                "is_game_over": getattr(metadata, 'is_game_over', False),
                "is_offseason": getattr(metadata, 'is_offseason', False)
            }

            # Cache permanently since game metadata doesn't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game metadata by game ID: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_game_position_types_by_game_id(game_id: str, sport: str = "nfl") -> Dict[str, Any]:
        """
        Get position types for a specific game.

        Args:
            game_id: Yahoo game ID
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Game position types information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"game_position_types/{game_id}/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)
            position_types = yahoo_query.get_game_position_types_by_game_id(int(game_id))

            positions_data = []
            if position_types:
                for position in position_types:
                    position_data = {
                        "type": str(getattr(position, 'type', 'Unknown')),
                        "display_name": str(getattr(position, 'display_name', 'Unknown')),
                        "is_only_display_stat": getattr(position, 'is_only_display_stat', False)
                    }
                    positions_data.append(position_data)

            result = {
                "game_id": game_id,
                "sport": sport,
                "position_types": positions_data,
                "total_position_types": len(positions_data)
            }

            # Cache permanently since position types don't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game position types by game ID: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_game_roster_positions_by_game_id(game_id: str, sport: str = "nfl") -> Dict[str, Any]:
        """
        Get roster positions for a specific game.

        Args:
            game_id: Yahoo game ID
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Game roster positions information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"game_roster_positions/{game_id}/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)
            roster_positions = yahoo_query.get_game_roster_positions_by_game_id(int(game_id))

            positions_data = []
            if roster_positions:
                for position in roster_positions:
                    position_data = {
                        "position": str(getattr(position, 'position', 'Unknown')),
                        "position_type": str(getattr(position, 'position_type', 'Unknown')),
                        "count": getattr(position, 'count', 0),
                        "is_bench": getattr(position, 'is_bench', False)
                    }
                    positions_data.append(position_data)

            result = {
                "game_id": game_id,
                "sport": sport,
                "roster_positions": positions_data,
                "total_roster_positions": len(positions_data)
            }

            # Cache permanently since roster positions don't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game roster positions by game ID: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_game_stat_categories_by_game_id(game_id: str, sport: str = "nfl") -> Dict[str, Any]:
        """
        Get stat categories for a specific game.

        Args:
            game_id: Yahoo game ID
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Game stat categories information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"game_stat_categories/{game_id}/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)
            stat_categories = yahoo_query.get_game_stat_categories_by_game_id(int(game_id))

            stats_data = []
            if stat_categories:
                for stat in stat_categories:
                    stat_data = {
                        "stat_id": getattr(stat, 'stat_id', 0),
                        "enabled": getattr(stat, 'enabled', False),
                        "name": str(getattr(stat, 'name', 'Unknown')),
                        "display_name": str(getattr(stat, 'display_name', 'Unknown')),
                        "sort_order": getattr(stat, 'sort_order', 0),
                        "position_type": str(getattr(stat, 'position_type', 'Unknown')),
                        "is_only_display_stat": getattr(stat, 'is_only_display_stat', False)
                    }
                    stats_data.append(stat_data)

            result = {
                "game_id": game_id,
                "sport": sport,
                "stat_categories": stats_data,
                "total_stat_categories": len(stats_data)
            }

            # Cache permanently since stat categories don't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game stat categories by game ID: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_game_weeks_by_game_id(game_id: str, sport: str = "nfl") -> Dict[str, Any]:
        """
        Get game weeks for a specific game.

        Args:
            game_id: Yahoo game ID
            sport: Sport code (nfl, nba, mlb, nhl)

        Returns:
            Game weeks information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"game_weeks/{game_id}/{sport}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            yahoo_query = get_yahoo_query("temp", app_state, game_id, sport)
            game_weeks = yahoo_query.get_game_weeks_by_game_id(int(game_id))

            weeks_data = []
            if game_weeks:
                for week in game_weeks:
                    week_data = {
                        "week": getattr(week, 'week', 0),
                        "start": str(getattr(week, 'start', 'Unknown')),
                        "end": str(getattr(week, 'end', 'Unknown')),
                        "display_name": str(getattr(week, 'display_name', 'Unknown'))
                    }
                    weeks_data.append(week_data)

            result = {
                "game_id": game_id,
                "sport": sport,
                "game_weeks": weeks_data,
                "total_weeks": len(weeks_data)
            }

            # Cache permanently since game weeks don't change
            cache_manager.set(cache_key, result, ttl=-1)

            return result

        except Exception as e:
            logger.error(f"Error getting game weeks by game ID: {e}")
            return {"error": str(e)}
