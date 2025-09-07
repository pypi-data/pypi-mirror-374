#!/usr/bin/env python3
"""
Implementation functions for MCP tools that can be imported and tested.

These are private implementation functions extracted from the MCP tool decorators
to enable proper testing and direct function access.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from yfpy import YahooFantasySportsQuery

from .enhancement_helpers import DataEnhancer

logger = logging.getLogger(__name__)


def _get_yahoo_query(league_id: str, game_id: Optional[str], sport: str, app_state: Dict[str, Any]) -> YahooFantasySportsQuery:
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


def get_league_info_impl(league_id: str, sport: str, season: Optional[str], app_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implementation of get_league_info MCP tool.
    
    Args:
        league_id: Yahoo league ID
        sport: Sport code (nfl, nba, mlb, nhl)
        season: Specific season year (optional)
        app_state: Application state containing cache_manager, auth_manager, etc.
        
    Returns:
        League information and settings
    """
    try:
        cache_manager = app_state["cache_manager"]

        # Check cache first
        if season:
            cached_data = cache_manager.get_historical_data(sport, season, league_id, "league_info")
        else:
            cached_data = cache_manager.get_current_data(sport, league_id, "league_info")

        if cached_data:
            return cached_data

        # Get game_id for specific season if provided
        game_id = None
        if season:
            game_id = app_state["game_ids"].get(sport, {}).get(season)
            if not game_id:
                return {"error": f"No game_id found for {sport} {season}"}

        yahoo_query = _get_yahoo_query(league_id, game_id, sport, app_state)
        league_info = yahoo_query.get_league_info()

        # Use DataEnhancer for consistent, readable league information
        data_enhancer = DataEnhancer(yahoo_query, cache_manager)
        enhanced_league_info = data_enhancer.enhance_league_info(league_info)

        result = {
            "league_id": league_id,
            "sport": sport,
            "season": season or "current",
            **enhanced_league_info
        }

        # Cache the result
        if season:
            cache_manager.set_historical_data(sport, season, league_id, "league_info", result)
        else:
            cache_manager.set_current_data(sport, league_id, "league_info", result)

        return result

    except Exception as e:
        logger.error(f"Error getting league info: {e}")
        return {"error": str(e)}


def get_standings_impl(league_id: str, sport: str, season: Optional[str], app_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implementation of get_standings MCP tool.
    
    Args:
        league_id: Yahoo league ID
        sport: Sport code (nfl, nba, mlb, nhl)
        season: Specific season year (optional)
        app_state: Application state containing cache_manager, auth_manager, etc.
        
    Returns:
        League standings information
    """
    try:
        cache_manager = app_state["cache_manager"]

        # Check cache first
        if season:
            cached_data = cache_manager.get_historical_data(sport, season, league_id, "standings")
        else:
            cached_data = cache_manager.get_current_data(sport, league_id, "standings")

        if cached_data:
            return cached_data

        # Get game_id for specific season if provided
        game_id = None
        if season:
            game_id = app_state["game_ids"].get(sport, {}).get(season)
            if not game_id:
                return {"error": f"No game_id found for {sport} {season}"}

        yahoo_query = _get_yahoo_query(league_id, game_id, sport, app_state)
        standings = yahoo_query.get_league_standings()

        # Use DataEnhancer for consistent, readable team results
        data_enhancer = DataEnhancer(yahoo_query, cache_manager)
        teams_data = data_enhancer.enhance_data_batch(standings.teams, 'team')

        result = {
            "league_id": league_id,
            "sport": sport,
            "season": season or "current",
            "teams": teams_data
        }

        # Cache the result
        if season:
            cache_manager.set_historical_data(sport, season, league_id, "standings", result)
        else:
            cache_manager.set_current_data(sport, league_id, "standings", result)

        return result

    except Exception as e:
        logger.error(f"Error getting standings: {e}")
        return {"error": str(e)}


def get_team_roster_impl(league_id: str, team_id: str, sport: str, season: Optional[str], app_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implementation of get_team_roster MCP tool.
    
    Args:
        league_id: Yahoo league ID
        team_id: Team ID within the league
        sport: Sport code (nfl, nba, mlb, nhl)
        season: Specific season year (optional)
        app_state: Application state containing cache_manager, auth_manager, etc.
        
    Returns:
        Team roster information
    """
    try:
        cache_manager = app_state["cache_manager"]

        # Check cache first
        cache_key_params = {"team_id": team_id}
        if season:
            cached_data = cache_manager.get_historical_data(
                sport, season, league_id, "team_roster", **cache_key_params)
        else:
            cached_data = cache_manager.get_current_data(sport, league_id, "team_roster", **cache_key_params)

        if cached_data:
            return cached_data

        # Get game_id for specific season if provided
        game_id = None
        if season:
            game_id = app_state["game_ids"].get(sport, {}).get(season)
            if not game_id:
                return {"error": f"No game_id found for {sport} {season}"}

        yahoo_query = _get_yahoo_query(league_id, game_id, sport, app_state)
        roster = yahoo_query.get_team_roster_by_week(team_id, 1)  # Default to week 1
        
        # Use DataEnhancer for proper data extraction
        data_enhancer = DataEnhancer(yahoo_query, cache_manager)
        players_data = []
        for player in roster:
            enhanced_player = data_enhancer.enhance_player_stats(player)
            player_data = {
                "player_id": enhanced_player.get("player_id", "Unknown"),
                "name": enhanced_player.get("player_name", "Unknown"),
                "position_type": enhanced_player.get("position_type", "Unknown"),
                "eligible_positions": enhanced_player.get("eligible_positions", []),
                "selected_position": enhanced_player.get("selected_position", {}),
                "team_abbr": enhanced_player.get("editorial_team_abbr", "Unknown")
            }
            players_data.append(player_data)

        result = {
            "league_id": league_id,
            "team_id": team_id,
            "sport": sport,
            "season": season or "current",
            "roster": {"players": players_data},
            "roster_size": len(players_data)
        }

        # Cache the result
        if season:
            cache_manager.set_historical_data(sport, season, league_id, "team_roster", result, **cache_key_params)
        else:
            cache_manager.set_current_data(sport, league_id, "team_roster", result, **cache_key_params)

        return result

    except Exception as e:
        logger.error(f"Error getting team roster: {e}")
        return {"error": str(e)}


def get_matchups_impl(league_id: str, sport: str, week: Optional[int], season: Optional[str], app_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implementation of get_matchups MCP tool.
    
    Args:
        league_id: Yahoo league ID
        sport: Sport code (nfl, nba, mlb, nhl)
        week: Week number (optional, uses current week if not provided)
        season: Specific season year (optional)
        app_state: Application state containing cache_manager, auth_manager, etc.
        
    Returns:
        Matchup information for the specified week
    """
    try:
        cache_manager = app_state["cache_manager"]

        # Check cache first
        cache_key_params = {"week": week} if week else {}
        if season:
            cached_data = cache_manager.get_historical_data(
                sport, season, league_id, "matchups", **cache_key_params)
        else:
            cached_data = cache_manager.get_current_data(sport, league_id, "matchups", **cache_key_params)

        if cached_data:
            return cached_data

        # Get game_id for specific season if provided
        game_id = None
        if season:
            game_id = app_state["game_ids"].get(sport, {}).get(season)
            if not game_id:
                return {"error": f"No game_id found for {sport} {season}"}

        yahoo_query = _get_yahoo_query(league_id, game_id, sport, app_state)

        # Get current week if not provided
        if not week:
            league = yahoo_query.get_league_info()
            week = getattr(league, 'current_week', 1)
        
        # Ensure week is an int for the API call
        week_int = int(week) if week is not None else 1
        matchups = yahoo_query.get_league_matchups_by_week(chosen_week=week_int)

        matchup_data = []
        for matchup in matchups:
            matchup_info: Dict[str, Any] = {
                "week": week_int,
                "is_playoffs": getattr(matchup, 'is_playoffs', False),
                "is_consolation": getattr(matchup, 'is_consolation', False),
                "teams": []
            }

            teams = getattr(matchup, 'teams', [])
            for team in teams:
                team_info = {
                    "team_id": getattr(team, 'team_id', 'Unknown'),
                    "name": getattr(team, 'name', 'Unknown'),
                    "points": getattr(team, 'points', 0.0),
                    "projected_points": getattr(team, 'projected_points', 0.0)
                }
                teams_list: Union[List[Dict[str, Any]], None] = matchup_info.get("teams")
                if isinstance(teams_list, list):
                    teams_list.append(team_info)

            matchup_data.append(matchup_info)

        result = {
            "league_id": league_id,
            "sport": sport,
            "season": season or "current",
            "week": week,
            "matchups": matchup_data,
            "total_matchups": len(matchup_data)
        }

        # Cache the result
        if season:
            cache_manager.set_historical_data(sport, season, league_id, "matchups", result, **cache_key_params)
        else:
            cache_manager.set_current_data(sport, league_id, "matchups", result, **cache_key_params)

        return result

    except Exception as e:
        logger.error(f"Error getting matchups: {e}")
        return {"error": str(e)}
