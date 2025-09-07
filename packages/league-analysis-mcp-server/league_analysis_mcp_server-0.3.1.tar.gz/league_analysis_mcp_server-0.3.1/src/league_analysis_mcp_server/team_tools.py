"""
MCP Team Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP
from .shared_utils import get_yahoo_query, handle_api_error
from .enhancement_helpers import get_player_name, DataEnhancer

logger = logging.getLogger(__name__)


def register_team_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register all MCP team tools."""


    @mcp.tool()
    def get_team_draft_results(league_id: str, team_id: str, sport: str = "nfl",
                               season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get draft results for a specific team.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team draft results information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_draft", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_draft", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            draft_results = yahoo_query.get_team_draft_results(team_id)

            picks_data = []
            # Handle both direct list and wrapped object cases
            if hasattr(draft_results, 'picks') and draft_results.picks:  # type: ignore
                picks_list = draft_results.picks  # type: ignore
            elif isinstance(draft_results, list):
                picks_list = draft_results
            else:
                picks_list = []
                
            if picks_list:
                for pick in picks_list:
                    pick_data = {
                        "pick": getattr(pick, 'pick', 0),
                        "round": getattr(pick, 'round', 0),
                        "team_key": str(getattr(pick, 'team_key', 'Unknown')),
                        "player_key": str(getattr(pick, 'player_key', 'Unknown')),
                        "cost": getattr(pick, 'cost', 0)
                    }
                    picks_data.append(pick_data)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "sport": sport,
                "season": season or "current",
                "total_picks": len(picks_data),
                "picks": picks_data
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "team_draft", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_draft", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team draft results: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_info(league_id: str, team_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information for a specific team.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_info", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_info", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            team = yahoo_query.get_team_info(team_id)

            result = {
                "league_id": league_id,
                "team_id": str(getattr(team, 'team_id', team_id)),
                "sport": sport,
                "season": season or "current",
                "team_key": str(getattr(team, 'team_key', 'Unknown')),
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
                    managers_list = result.get("managers")
                    if isinstance(managers_list, list):
                        managers_list.append(manager_data)

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "team_info", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_info", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team info: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_matchups(league_id: str, team_id: str, sport: str = "nfl",
                          season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all matchups for a specific team.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team matchups information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_matchups", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_matchups", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            matchups = yahoo_query.get_team_matchups(team_id)

            matchups_data = []
            if matchups:
                for matchup in matchups:
                    teams_data = []
                    if hasattr(matchup, 'teams') and matchup.teams:
                        for team in matchup.teams:
                            team_data = {
                                "team_key": str(
                                    getattr(
                                        team,
                                        'team_key',
                                        'Unknown')),
                                "team_id": str(
                                    getattr(
                                        team,
                                        'team_id',
                                        'Unknown')),
                                "name": str(
                                    getattr(
                                        team,
                                        'name',
                                        'Unknown')).replace(
                                    'b"',
                                    '').replace(
                                    '"',
                                    '').replace(
                                        "b'",
                                        "").replace(
                                            "'",
                                            ""),
                                "team_points": getattr(
                                    team,
                                    'team_points',
                                    {}),
                                "team_projected_points": getattr(
                                    team,
                                    'team_projected_points',
                                    {})}
                            teams_data.append(team_data)

                    matchup_data = {
                        "week": getattr(matchup, 'week', 0),
                        "week_start": str(getattr(matchup, 'week_start', 'Unknown')),
                        "week_end": str(getattr(matchup, 'week_end', 'Unknown')),
                        "status": str(getattr(matchup, 'status', 'Unknown')),
                        "is_playoffs": getattr(matchup, 'is_playoffs', False),
                        "is_consolation": getattr(matchup, 'is_consolation', False),
                        "is_tied": getattr(matchup, 'is_tied', False),
                        "winner_team_key": str(getattr(matchup, 'winner_team_key', 'Unknown')),
                        "teams": teams_data
                    }
                    matchups_data.append(matchup_data)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "sport": sport,
                "season": season or "current",
                "matchups": matchups_data,
                "total_matchups": len(matchups_data)
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "team_matchups", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_matchups", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team matchups: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_metadata(league_id: str, team_id: str, sport: str = "nfl",
                          season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get team metadata and configuration.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team metadata information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/team_metadata/{team_id}/{season or 'current'}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            metadata = yahoo_query.get_team_metadata(team_id)

            result = {
                "league_id": league_id,
                "team_id": str(getattr(metadata, 'team_id', team_id)),
                "sport": sport,
                "season": season or "current",
                "team_key": str(getattr(metadata, 'team_key', 'Unknown')),
                "name": str(getattr(metadata, 'name', 'Unknown')),
                "is_owned_by_current_login": getattr(metadata, 'is_owned_by_current_login', False),
                "url": str(getattr(metadata, 'url', 'Unknown')),
                "team_logos": getattr(metadata, 'team_logos', []),
                "waiver_priority": getattr(metadata, 'waiver_priority', 0),
                "number_of_moves": getattr(metadata, 'number_of_moves', 0),
                "number_of_trades": getattr(metadata, 'number_of_trades', 0),
                "roster_adds": getattr(metadata, 'roster_adds', {}),
                "league_scoring_type": str(getattr(metadata, 'league_scoring_type', 'Unknown')),
                "has_draft_grade": getattr(metadata, 'has_draft_grade', False),
                "auction_budget_total": getattr(metadata, 'auction_budget_total', 0),
                "auction_budget_spent": getattr(metadata, 'auction_budget_spent', 0)
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting team metadata: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_roster_player_info_by_date(league_id: str,
                                            team_id: str,
                                            selected_date: str,
                                            sport: str = "nfl",
                                            season: Optional[str] = None) -> Dict[str,
                                                                                  Any]:
        """
        Get team roster player information for a specific date.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            selected_date: Date in YYYY-MM-DD format
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team roster player information by date
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id, "date": selected_date}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_roster_date", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_roster_date", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            roster = yahoo_query.get_team_roster_player_info_by_date(team_id=team_id, chosen_date=selected_date)

            players_data = []
            if roster:
                for player in roster:
                    player_data = {
                        "player_key": str(getattr(player, 'player_key', 'Unknown')),
                        "player_id": str(getattr(player, 'player_id', 'Unknown')),
                        "name": get_player_name(player),
                        "editorial_player_key": str(getattr(player, 'editorial_player_key', 'Unknown')),
                        "editorial_team_key": str(getattr(player, 'editorial_team_key', 'Unknown')),
                        "editorial_team_full_name": str(getattr(player, 'editorial_team_full_name', 'Unknown')),
                        "editorial_team_abbr": str(getattr(player, 'editorial_team_abbr', 'Unknown')),
                        "uniform_number": getattr(player, 'uniform_number', 0),
                        "display_position": str(getattr(player, 'display_position', 'Unknown')),
                        "primary_position": str(getattr(player, 'primary_position', 'Unknown')),
                        "position_type": str(getattr(player, 'position_type', 'Unknown')),
                        "eligible_positions": getattr(player, 'eligible_positions', []),
                        "selected_position": getattr(player, 'selected_position', {}),
                        "is_undroppable": getattr(player, 'is_undroppable', False),
                        "status": str(getattr(player, 'status', 'Unknown')),
                        "status_full": str(getattr(player, 'status_full', 'Unknown')),
                        "image_url": str(getattr(player, 'image_url', 'Unknown'))
                    }
                    players_data.append(player_data)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "date": selected_date,
                "sport": sport,
                "season": season or "current",
                "total_players": len(players_data),
                "players": players_data
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(
                    sport, season, league_id, "team_roster_date", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_roster_date", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team roster player info by date: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_roster_player_info_by_week(league_id: str, team_id: str, week: int,
                                            sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get team roster player information for a specific week.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            week: Week number
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team roster player information by week
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id, "week": week}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_roster_week", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_roster_week", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            roster = yahoo_query.get_team_roster_player_info_by_week(team_id=team_id, chosen_week=week)

            players_data = []
            if roster:
                for player in roster:
                    player_data = {
                        "player_key": str(getattr(player, 'player_key', 'Unknown')),
                        "player_id": str(getattr(player, 'player_id', 'Unknown')),
                        "name": get_player_name(player),
                        "editorial_player_key": str(getattr(player, 'editorial_player_key', 'Unknown')),
                        "editorial_team_key": str(getattr(player, 'editorial_team_key', 'Unknown')),
                        "editorial_team_full_name": str(getattr(player, 'editorial_team_full_name', 'Unknown')),
                        "editorial_team_abbr": str(getattr(player, 'editorial_team_abbr', 'Unknown')),
                        "uniform_number": getattr(player, 'uniform_number', 0),
                        "display_position": str(getattr(player, 'display_position', 'Unknown')),
                        "primary_position": str(getattr(player, 'primary_position', 'Unknown')),
                        "position_type": str(getattr(player, 'position_type', 'Unknown')),
                        "eligible_positions": getattr(player, 'eligible_positions', []),
                        "selected_position": getattr(player, 'selected_position', {}),
                        "is_undroppable": getattr(player, 'is_undroppable', False),
                        "status": str(getattr(player, 'status', 'Unknown')),
                        "status_full": str(getattr(player, 'status_full', 'Unknown')),
                        "image_url": str(getattr(player, 'image_url', 'Unknown'))
                    }
                    players_data.append(player_data)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "week": week,
                "sport": sport,
                "season": season or "current",
                "total_players": len(players_data),
                "players": players_data
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(
                    sport, season, league_id, "team_roster_week", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_roster_week", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team roster player info by week: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_roster_player_stats(league_id: str, team_id: str, sport: str = "nfl",
                                     season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get team roster player statistics.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team roster player statistics
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_roster_stats", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_roster_stats", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            roster = yahoo_query.get_team_roster_player_stats(team_id)

            players_data = []
            if roster:
                for player in roster:
                    player_data = {
                        "player_key": str(getattr(player, 'player_key', 'Unknown')),
                        "player_id": str(getattr(player, 'player_id', 'Unknown')),
                        "name": get_player_name(player),
                        "editorial_team_abbr": str(getattr(player, 'editorial_team_abbr', 'Unknown')),
                        "display_position": str(getattr(player, 'display_position', 'Unknown')),
                        "selected_position": getattr(player, 'selected_position', {}),
                        "player_stats": getattr(player, 'player_stats', {}),
                        "player_points": getattr(player, 'player_points', {})
                    }
                    players_data.append(player_data)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "sport": sport,
                "season": season or "current",
                "total_players": len(players_data),
                "players": players_data
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(
                    sport, season, league_id, "team_roster_stats", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_roster_stats", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team roster player stats: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_roster_player_stats_by_week(league_id: str,
                                             team_id: str,
                                             week: int,
                                             sport: str = "nfl",
                                             season: Optional[str] = None) -> Dict[str,
                                                                                   Any]:
        """
        Get team roster player statistics for a specific week.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            week: Week number
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team roster player statistics by week
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id, "week": week}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_roster_stats_week", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(
                    sport, league_id, "team_roster_stats_week", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            roster = yahoo_query.get_team_roster_player_stats_by_week(team_id=team_id, chosen_week=week)

            players_data = []
            if roster:
                for player in roster:
                    player_data = {
                        "player_key": str(getattr(player, 'player_key', 'Unknown')),
                        "player_id": str(getattr(player, 'player_id', 'Unknown')),
                        "name": get_player_name(player),
                        "editorial_team_abbr": str(getattr(player, 'editorial_team_abbr', 'Unknown')),
                        "display_position": str(getattr(player, 'display_position', 'Unknown')),
                        "selected_position": getattr(player, 'selected_position', {}),
                        "player_stats": getattr(player, 'player_stats', {}),
                        "player_points": getattr(player, 'player_points', {})
                    }
                    players_data.append(player_data)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "week": week,
                "sport": sport,
                "season": season or "current",
                "total_players": len(players_data),
                "players": players_data
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(
                    sport,
                    season,
                    league_id,
                    "team_roster_stats_week",
                    result,
                    **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_roster_stats_week", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team roster player stats by week: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_standings(league_id: str, team_id: str, sport: str = "nfl",
                           season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get standings information for a specific team.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team standings information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_standings", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_standings", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            team_standings = yahoo_query.get_team_standings(team_id)

            # Use DataEnhancer for proper data extraction
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            team_name = data_enhancer._decode_name_bytes(getattr(team_standings, 'name', 'Unknown'))

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "sport": sport,
                "season": season or "current",
                "team_key": str(getattr(team_standings, 'team_key', 'Unknown')),
                "name": team_name,
                "rank": getattr(team_standings, 'rank', 0),
                "wins": getattr(team_standings, 'wins', 0),
                "losses": getattr(team_standings, 'losses', 0),
                "ties": getattr(team_standings, 'ties', 0),
                "win_percentage": getattr(team_standings, 'win_percentage', 0.0),
                "games_back": getattr(team_standings, 'games_back', 0.0),
                "points_for": getattr(team_standings, 'points_for', 0.0),
                "points_against": getattr(team_standings, 'points_against', 0.0)
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(
                    sport, season, league_id, "team_standings", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_standings", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team standings: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_stats(league_id: str, team_id: str, sport: str = "nfl",
                       season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a specific team.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team statistics information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_stats", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_stats", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            team_stats = yahoo_query.get_team_stats(team_id)

            # Use DataEnhancer for proper data extraction
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            team_name = data_enhancer._decode_name_bytes(getattr(team_stats, 'name', 'Unknown'))

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "sport": sport,
                "season": season or "current",
                "team_key": str(getattr(team_stats, 'team_key', 'Unknown')),
                "name": team_name,
                "team_stats": getattr(
                    team_stats,
                    'team_stats',
                    {}),
                "team_points": getattr(
                    team_stats,
                    'team_points',
                    {}),
                "team_remaining_games": getattr(
                    team_stats,
                    'team_remaining_games',
                    {})}

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "team_stats", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_stats", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_team_stats_by_week(league_id: str, team_id: str, week: int, sport: str = "nfl",
                               season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a specific team by week.

        Args:
            league_id: Yahoo league ID
            team_id: Yahoo team ID
            week: Week number
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Team statistics by week
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"team_id": team_id, "week": week}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "team_stats_week", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_stats_week", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, app_state, game_id, sport)
            team_stats = yahoo_query.get_team_stats_by_week(team_id=team_id, chosen_week=week)

            result = {
                "league_id": league_id,
                "team_id": team_id,
                "week": week,
                "sport": sport,
                "season": season or "current",
                "team_key": str(
                    getattr(
                        team_stats,
                        'team_key',
                        'Unknown')),
                "name": str(
                    getattr(
                        team_stats,
                        'name',
                        'Unknown')).replace(
                    'b"',
                    '').replace(
                            '"',
                            '').replace(
                                "b'",
                                "").replace(
                                    "'",
                                    ""),
                "team_stats": getattr(
                    team_stats,
                    'team_stats',
                    {}),
                "team_points": getattr(
                    team_stats,
                    'team_points',
                    {}),
                "team_remaining_games": getattr(
                    team_stats,
                    'team_remaining_games',
                    {})}

            # Cache the result
            if season:
                cache_manager.set_historical_data(
                    sport, season, league_id, "team_stats_week", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_stats_week", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting team stats by week: {e}")
            return {"error": str(e)}
