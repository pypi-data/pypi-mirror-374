"""
MCP Player Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP
from .enhancement_helpers import DataEnhancer, get_player_name

logger = logging.getLogger(__name__)


def register_player_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register all MCP player tools."""

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
    def get_player_draft_analysis(league_id: str, player_key: str, sport: str = "nfl",
                                  season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get draft analysis for a specific player.

        Args:
            league_id: Yahoo league ID
            player_key: Yahoo player key
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Player draft analysis information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/player_draft_analysis/{player_key}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            draft_analysis = yahoo_query.get_player_draft_analysis(player_key)

            # Use DataEnhancer for consistent, readable draft analysis
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            enhanced_player = data_enhancer.enhance_player_stats(draft_analysis)

            # Add draft-specific analysis fields
            draft_data = {
                "average_pick": getattr(draft_analysis, 'average_pick', 0.0),
                "average_round": getattr(draft_analysis, 'average_round', 0.0),
                "average_cost": getattr(draft_analysis, 'average_cost', 0.0),
                "percent_drafted": getattr(draft_analysis, 'percent_drafted', 0.0)
            }

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                **enhanced_player,
                **draft_data
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting player draft analysis: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_player_ownership(league_id: str, player_key: str, sport: str = "nfl",
                             season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get ownership information for a specific player.

        Args:
            league_id: Yahoo league ID
            player_key: Yahoo player key
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Player ownership information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/player_ownership/{player_key}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            ownership = yahoo_query.get_player_ownership(player_key)

            # Use DataEnhancer for consistent, readable ownership data
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            enhanced_ownership = data_enhancer.enhance_player_stats(ownership)

            # Add ownership-specific fields
            ownership_data = {
                "ownership_type": str(getattr(ownership, 'ownership_type', 'Unknown')),
                "owner_team_key": str(getattr(ownership, 'owner_team_key', 'Unknown')),
                "owner_team_name": str(getattr(ownership, 'owner_team_name', 'Unknown')),
                "date_added": str(getattr(ownership, 'date_added', 'Unknown')),
                "date_dropped": str(getattr(ownership, 'date_dropped', 'Unknown'))
            }

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                **enhanced_ownership,
                **ownership_data
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting player ownership: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_player_percent_owned_by_week(league_id: str, player_key: str, week: int,
                                         sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weekly ownership percentage for a specific player.

        Args:
            league_id: Yahoo league ID
            player_key: Yahoo player key
            week: Week number
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Player weekly ownership percentage
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/player_percent_owned/{player_key}/{week}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            ownership = yahoo_query.get_player_percent_owned_by_week(player_key=player_key, chosen_week=week)

            result = {
                "league_id": league_id,
                "player_key": player_key,
                "week": week,
                "sport": sport,
                "season": season or "current",
                "coverage_type": str(getattr(ownership, 'coverage_type', 'Unknown')),
                "coverage_value": getattr(ownership, 'coverage_value', week),
                "percent_owned": {
                    "coverage_type": str(getattr(getattr(ownership, 'percent_owned', {}), 'coverage_type', 'Unknown')),
                    "week": getattr(getattr(ownership, 'percent_owned', {}), 'week', week),
                    "value": getattr(getattr(ownership, 'percent_owned', {}), 'value', 0.0)
                }
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting player percent owned by week: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_player_stats_by_date(league_id: str, player_key: str, selected_date: str,
                                 sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get player statistics for a specific date.

        Args:
            league_id: Yahoo league ID
            player_key: Yahoo player key
            selected_date: Date in YYYY-MM-DD format
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Player statistics by date
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/player_stats_date/{player_key}/{selected_date}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            stats = yahoo_query.get_player_stats_by_date(player_key=player_key, chosen_date=selected_date)

            result = {
                "league_id": league_id,
                "player_key": player_key,
                "date": selected_date,
                "sport": sport,
                "season": season or "current",
                "player_id": str(getattr(stats, 'player_id', 'Unknown')),
                "name": get_player_name(stats),
                "editorial_team_abbr": str(getattr(stats, 'editorial_team_abbr', 'Unknown')),
                "display_position": str(getattr(stats, 'display_position', 'Unknown')),
                "player_stats": getattr(stats, 'player_stats', {}),
                "player_points": getattr(stats, 'player_points', {})
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting player stats by date: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_player_stats_by_week(league_id: str, player_key: str, week: int,
                                 sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get player statistics for a specific week.

        Args:
            league_id: Yahoo league ID
            player_key: Yahoo player key
            week: Week number
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Player statistics by week
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/player_stats_week/{player_key}/{week}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            stats = yahoo_query.get_player_stats_by_week(player_key=player_key, chosen_week=week)

            result = {
                "league_id": league_id,
                "player_key": player_key,
                "week": week,
                "sport": sport,
                "season": season or "current",
                "player_id": str(getattr(stats, 'player_id', 'Unknown')),
                "name": get_player_name(stats),
                "editorial_team_abbr": str(getattr(stats, 'editorial_team_abbr', 'Unknown')),
                "display_position": str(getattr(stats, 'display_position', 'Unknown')),
                "player_stats": getattr(stats, 'player_stats', {}),
                "player_points": getattr(stats, 'player_points', {})
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting player stats by week: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_player_stats_for_season(league_id: str, player_key: str, sport: str = "nfl",
                                    season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get player statistics for an entire season.

        Args:
            league_id: Yahoo league ID
            player_key: Yahoo player key
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Player statistics for season
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/player_stats_season/{player_key}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            stats = yahoo_query.get_player_stats_for_season(player_key)

            # Use DataEnhancer for consistent, readable player stats
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            enhanced_stats = data_enhancer.enhance_player_stats(stats)

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                **enhanced_stats
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting player stats for season: {e}")
            return {"error": str(e)}
