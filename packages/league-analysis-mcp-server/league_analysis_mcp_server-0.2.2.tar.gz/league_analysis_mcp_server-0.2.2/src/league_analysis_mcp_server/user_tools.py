"""
MCP User Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_user_tools(mcp: FastMCP, app_state: Dict[str, Any]) -> None:
    """Register all MCP user tools."""

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

            yahoo_query = get_yahoo_query("temp", game_id, sport)  # League ID not needed for user games
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
            logger.error(f"Error getting user games: {e}")
            return {"error": str(e)}

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

            yahoo_query = get_yahoo_query("temp", game_id, sport)  # League ID not needed for user teams
            user_teams = yahoo_query.get_user_teams()

            teams_data = []
            if user_teams:
                for team in user_teams:
                    team_data = {
                        "team_key": str(getattr(team, 'team_key', 'Unknown')),
                        "team_id": str(getattr(team, 'team_id', 'Unknown')),
                        "name": (
                            str(getattr(team, 'name', 'Unknown'))
                            .replace('b"', '').replace('"', '')
                            .replace("b'", "").replace("'", "")
                        ),
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
            logger.error(f"Error getting user teams: {e}")
            return {"error": str(e)}
