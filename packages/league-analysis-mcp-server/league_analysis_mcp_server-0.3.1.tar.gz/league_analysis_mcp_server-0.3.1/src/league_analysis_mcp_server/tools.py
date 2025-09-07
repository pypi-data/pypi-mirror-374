"""
MCP Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, Optional, List, Union

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP
from .enhancement_helpers import DataEnhancer, get_player_name
from .historical import register_historical_tools
from .analytics import register_analytics_tools

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, app_state: Dict[str, Any]) -> None:
    """Register all MCP tools."""

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
    def get_user_leagues(sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all leagues the authenticated user belongs to for a specific sport.

        Args:
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional, uses current if not provided)

        Returns:
            Dict containing user's leagues information
        """
        cache_manager = app_state["cache_manager"]

        try:
            # Create cache key
            cache_key = f"{sport}/user_leagues/{season or 'current'}"

            # Check cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return cached_result

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            # Create temporary query to get user leagues
            auth_manager = app_state["auth_manager"]
            if not auth_manager.is_configured():
                raise ValueError("Yahoo authentication not configured. Run check_setup_status() to begin setup.")

            auth_credentials = auth_manager.get_auth_credentials()

            # Use game_id if provided, otherwise use current season
            if game_id:
                query_params = {**auth_credentials, 'game_id': game_id}
            else:
                query_params = {**auth_credentials, 'game_code': sport}

            yahoo_query = YahooFantasySportsQuery(
                league_id="temp",  # Temporary, not needed for user leagues
                **query_params
            )

            # Get user's leagues
            leagues = yahoo_query.get_user_leagues_by_game_key(sport)

            leagues_data = []
            for league in leagues:
                league_data = {
                    "league_id": str(
                        getattr(
                            league, 'league_id', 'Unknown')), "name": str(
                        getattr(
                            league, 'name', 'Unknown')).replace(
                        'b"', '').replace(
                            '"', '').replace(
                                "b'", "").replace(
                                    "'", ""), "num_teams": getattr(
                                        league, 'num_teams', 0), "season": getattr(
                                            league, 'season', 'Unknown'), "league_type": getattr(
                                                league, 'league_type', 'Unknown'), "scoring_type": getattr(
                                                    league, 'scoring_type', 'Unknown'), "current_week": getattr(
                                                        league, 'current_week', 1), "start_week": getattr(
                                                            league, 'start_week', 1), "end_week": getattr(
                                                                league, 'end_week', 17)}
                leagues_data.append(league_data)

            result = {
                "sport": sport,
                "season": season or "current",
                "total_leagues": len(leagues_data),
                "leagues": leagues_data
            }

            # Cache the result (current data)
            if season:
                cache_manager.set(cache_key, result, ttl=-1)  # Historical data - permanent cache
            else:
                cache_manager.set(cache_key, result, ttl=300)  # Current data - 5 min cache

            return result

        except Exception as e:
            logger.error(f"Error getting user leagues: {e}")
            return {"error": f"Failed to retrieve user leagues: {str(e)}"}

    @mcp.tool()
    def get_league_info(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get basic league information and settings.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional, uses current if not provided)

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

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
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

    @mcp.tool()
    def get_standings(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current league standings.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

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

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            standings = yahoo_query.get_league_standings()

            # Use DataEnhancer for consistent, readable team results
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            teams_data = data_enhancer.enhance_data_batch(standings.teams, 'team')

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "teams": teams_data,
                "total_teams": len(teams_data)
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

    @mcp.tool()
    def get_team_roster(league_id: str, team_id: str, sport: str = "nfl",
                        season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get roster for a specific team.

        Args:
            league_id: Yahoo league ID
            team_id: Team ID within the league
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

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

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
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
                "roster": players_data,
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

    @mcp.tool()
    def get_matchups(league_id: str, sport: str = "nfl", week: Optional[int] = None,
                     season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get matchups for a specific week.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            week: Week number (optional, uses current week if not provided)
            season: Specific season year (optional)

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

            yahoo_query = get_yahoo_query(league_id, game_id, sport)

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

    @mcp.tool()
    def get_league_draft_results(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current season draft results for a league.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Draft results information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            if season:
                cached_data = cache_manager.get_historical_data(sport, season, league_id, "draft_results")
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "draft_results")
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            draft_results = yahoo_query.get_league_draft_results()

            picks_data = []
            if draft_results:
                # Use DataEnhancer for consistent, readable results
                data_enhancer = DataEnhancer(yahoo_query, cache_manager)
                # Convert Data object to list for enhance_data_batch
                draft_list = list(draft_results) if draft_results else []
                picks_data = data_enhancer.enhance_data_batch(draft_list, 'draft_pick')

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "total_picks": len(picks_data),
                "picks": picks_data
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "draft_results", result)
            else:
                cache_manager.set_current_data(sport, league_id, "draft_results", result)

            return result

        except Exception as e:
            logger.error(f"Error getting league draft results: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_enhanced_draft_results(league_id: str, max_picks: int = 24, sport: str = "nfl",
                                   season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get enhanced draft results with player names, positions, and team information.
        Limited number of picks to avoid rate limiting.

        Args:
            league_id: Yahoo league ID
            max_picks: Maximum number of picks to retrieve with full player info (default: 24 = 2 rounds)
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Enhanced draft results with player names and team information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"enhanced_draft_results_{max_picks}"
            if season:
                cached_data = cache_manager.get_historical_data(sport, season, league_id, cache_key)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, cache_key)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            draft_results = yahoo_query.get_league_draft_results()

            if not draft_results:
                return {"error": "No draft results found"}

            # Use DataEnhancer for consistent, readable results
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)

            # Get team names for use in both enhancement paths
            team_names = data_enhancer.get_team_names()

            # Process picks with enhanced information (limited by max_picks to avoid rate limiting)
            enhanced_picks = []
            basic_picks = []

            for i, pick in enumerate(draft_results):
                if i < max_picks:
                    # Full enhancement for first max_picks
                    enhanced_pick = data_enhancer.enhance_draft_pick(pick)
                    enhanced_picks.append(enhanced_pick)
                else:
                    # Basic enhancement for remaining picks (no player API calls)
                    basic_pick = {
                        "pick": getattr(pick, 'pick', 0),
                        "round": getattr(pick, 'round', 0),
                        "team_key": str(getattr(pick, 'team_key', 'Unknown')),
                        "team_name": team_names.get(getattr(pick, 'team_key', ''), 'Unknown Team'),
                        "player_key": str(getattr(pick, 'player_key', 'Unknown')),
                        "cost": getattr(pick, 'cost', 0),
                        "player_name": f'Player {getattr(pick, "player_key", "Unknown")}',
                        "player_position": 'Unknown',
                        "player_team": 'Unknown'
                    }
                    basic_picks.append(basic_pick)

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "total_picks": len(draft_results),
                "enhanced_picks_count": len(enhanced_picks),
                "enhanced_picks": enhanced_picks,
                "remaining_picks_count": len(basic_picks),
                "remaining_picks": basic_picks,
                "team_names": team_names
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, cache_key, result)
            else:
                cache_manager.set_current_data(sport, league_id, cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Error getting enhanced draft results: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_league_key(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get league key for a specific league.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            League key information
        """
        try:
            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            league_key = yahoo_query.get_league_key()

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "league_key": str(league_key)
            }

            return result

        except Exception as e:
            logger.error(f"Error getting league key: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_league_metadata(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed league metadata and configuration.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            League metadata information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/metadata/{season or 'current'}"
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
            metadata = yahoo_query.get_league_metadata()

            # Use DataEnhancer for consistent, readable metadata
            data_enhancer = DataEnhancer(yahoo_query, cache_manager)
            data_enhancer.enhance_league_info(metadata)

            result = {
                "league_id": str(getattr(metadata, 'league_id', league_id)),
                "sport": sport,
                "league_key": str(getattr(metadata, 'league_key', 'Unknown')),
                "name": str(getattr(metadata, 'name', 'Unknown')),
                "url": str(getattr(metadata, 'url', 'Unknown')),
                "logo_url": str(getattr(metadata, 'logo_url', 'Unknown')),
                "password": str(getattr(metadata, 'password', 'Unknown')),
                "draft_status": str(getattr(metadata, 'draft_status', 'Unknown')),
                "num_teams": getattr(metadata, 'num_teams', 0),
                "edit_key": getattr(metadata, 'edit_key', 'Unknown'),
                "weekly_deadline": str(getattr(metadata, 'weekly_deadline', 'Unknown')),
                "league_update_timestamp": str(getattr(metadata, 'league_update_timestamp', 'Unknown')),
                "scoring_type": str(getattr(metadata, 'scoring_type', 'Unknown')),
                "league_type": str(getattr(metadata, 'league_type', 'Unknown')),
                "renew": str(getattr(metadata, 'renew', 'Unknown')),
                "renewed": str(getattr(metadata, 'renewed', 'Unknown')),
                "iris_group_chat_id": str(getattr(metadata, 'iris_group_chat_id', 'Unknown')),
                "allow_add_to_dl_extra_pos": getattr(metadata, 'allow_add_to_dl_extra_pos', 0),
                "is_pro_league": str(getattr(metadata, 'is_pro_league', 'Unknown')),
                "is_cash_league": str(getattr(metadata, 'is_cash_league', 'Unknown')),
                "current_week": getattr(metadata, 'current_week', 1),
                "start_week": getattr(metadata, 'start_week', 1),
                "start_date": str(getattr(metadata, 'start_date', 'Unknown')),
                "end_week": getattr(metadata, 'end_week', 17),
                "end_date": str(getattr(metadata, 'end_date', 'Unknown')),
                "game_code": str(getattr(metadata, 'game_code', sport)),
                "season": str(getattr(metadata, 'season', season or 'current'))
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting league metadata: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_league_players(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all available players in a league.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            League players information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/players/{season or 'current'}"
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
            players = yahoo_query.get_league_players()

            players_data = []
            # Handle both direct list and wrapped object cases
            if hasattr(players, 'players') and players.players:  # type: ignore
                players_list = players.players  # type: ignore
            elif isinstance(players, list):
                players_list = players
            else:
                players_list = []
                
            if players_list:
                for player in players_list:
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
                        "has_player_notes": getattr(player, 'has_player_notes', False),
                        "player_notes_last_timestamp": getattr(player, 'player_notes_last_timestamp', 0),
                        "image_url": str(getattr(player, 'image_url', 'Unknown')),
                        "is_undroppable": getattr(player, 'is_undroppable', False),
                        "status": str(getattr(player, 'status', 'Unknown')),
                        "status_full": str(getattr(player, 'status_full', 'Unknown'))
                    }
                    players_data.append(player_data)

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "total_players": len(players_data),
                "players": players_data
            }

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting league players: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_league_scoreboard_by_week(league_id: str, week: int, sport: str = "nfl",
                                      season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get league scoreboard for a specific week.

        Args:
            league_id: Yahoo league ID
            week: Week number
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            Weekly scoreboard information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key_params = {"week": week}
            if season:
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "scoreboard", **cache_key_params)
                if cached_data:
                    return cached_data
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "scoreboard", **cache_key_params)
                if cached_data:
                    return cached_data

            # Get game_id if specific season requested
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}

            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            scoreboard = yahoo_query.get_league_scoreboard_by_week(chosen_week=week)

            matchups_data = []
            if hasattr(scoreboard, 'matchups') and scoreboard.matchups:
                for matchup in scoreboard.matchups:
                    teams_data = []
                    if hasattr(matchup, 'teams') and matchup.teams:
                        for team in matchup.teams:
                            team_data = {
                                "team_key": str(getattr(team, 'team_key', 'Unknown')),
                                "team_id": str(getattr(team, 'team_id', 'Unknown')),
                                "name": (
                                    str(getattr(team, 'name', 'Unknown'))
                                    .replace('b"', '').replace('"', '')
                                    .replace("b'", "").replace("'", "")
                                ),
                                "team_points": {
                                    "coverage_type": str(
                                        getattr(getattr(team, 'team_points', {}), 'coverage_type', 'Unknown')
                                    ),
                                    "week": getattr(getattr(team, 'team_points', {}), 'week', week),
                                    "total": getattr(getattr(team, 'team_points', {}), 'total', 0.0)
                                },
                                "team_projected_points": {
                                    "coverage_type": str(
                                        getattr(getattr(team, 'team_projected_points', {}), 'coverage_type', 'Unknown')
                                    ),
                                    "week": getattr(getattr(team, 'team_projected_points', {}), 'week', week),
                                    "total": getattr(getattr(team, 'team_projected_points', {}), 'total', 0.0)
                                }
                            }
                            teams_data.append(team_data)

                    matchup_data = {
                        "week": week,
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
                "sport": sport,
                "season": season or "current",
                "week": week,
                "matchups": matchups_data,
                "total_matchups": len(matchups_data)
            }

            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "scoreboard", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "scoreboard", result, **cache_key_params)

            return result

        except Exception as e:
            logger.error(f"Error getting league scoreboard: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_league_settings(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get league settings and configuration.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)

        Returns:
            League settings information
        """
        try:
            cache_manager = app_state["cache_manager"]

            # Check cache first
            cache_key = f"{sport}/{league_id}/settings/{season or 'current'}"
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
            settings = yahoo_query.get_league_settings()

            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "draft_type": str(getattr(settings, 'draft_type', 'Unknown')),
                "is_auction_draft": getattr(settings, 'is_auction_draft', False),
                "scoring_type": str(getattr(settings, 'scoring_type', 'Unknown')),
                "uses_playoff": getattr(settings, 'uses_playoff', False),
                "has_playoff_consolation_games": getattr(settings, 'has_playoff_consolation_games', False),
                "playoff_start_week": getattr(settings, 'playoff_start_week', 0),
                "uses_playoff_reseeding": getattr(settings, 'uses_playoff_reseeding', False),
                "uses_lock_eliminated_teams": getattr(settings, 'uses_lock_eliminated_teams', False),
                "num_playoff_teams": getattr(settings, 'num_playoff_teams', 0),
                "num_playoff_consolation_teams": getattr(settings, 'num_playoff_consolation_teams', 0),
                "has_multiweek_championship": getattr(settings, 'has_multiweek_championship', False),
                "waiver_type": str(getattr(settings, 'waiver_type', 'Unknown')),
                "waiver_rule": str(getattr(settings, 'waiver_rule', 'Unknown')),
                "uses_faab": getattr(settings, 'uses_faab', False),
                "draft_time": str(getattr(settings, 'draft_time', 'Unknown')),
                "draft_pick_time": getattr(settings, 'draft_pick_time', 0),
                "post_draft_players": str(getattr(settings, 'post_draft_players', 'Unknown')),
                "max_teams": getattr(settings, 'max_teams', 0),
                "waiver_time": getattr(settings, 'waiver_time', 0),
                "trade_end_date": str(getattr(settings, 'trade_end_date', 'Unknown')),
                "trade_ratify_type": str(getattr(settings, 'trade_ratify_type', 'Unknown')),
                "trade_reject_time": getattr(settings, 'trade_reject_time', 0),
                "player_pool": str(getattr(settings, 'player_pool', 'Unknown')),
                "cant_cut_list": str(getattr(settings, 'cant_cut_list', 'Unknown')),
                "draft_together": getattr(settings, 'draft_together', False),
                "sendbird_channel_url": str(getattr(settings, 'sendbird_channel_url', 'Unknown')),
                "pickem_enabled": getattr(settings, 'pickem_enabled', False),
                "uses_fractional_points": getattr(settings, 'uses_fractional_points', False),
                "uses_negative_points": getattr(settings, 'uses_negative_points', False)
            }

            # Add roster positions if available
            if hasattr(settings, 'roster_positions') and settings.roster_positions:
                roster_positions = []
                for position in settings.roster_positions:
                    position_data = {
                        "position": str(getattr(position, 'position', 'Unknown')),
                        "position_type": str(getattr(position, 'position_type', 'Unknown')),
                        "count": getattr(position, 'count', 0)
                    }
                    roster_positions.append(position_data)
                result["roster_positions"] = roster_positions

            # Add stat categories if available
            if hasattr(settings, 'stat_categories') and settings.stat_categories:
                stat_categories = []
                for stat in settings.stat_categories:
                    stat_data = {
                        "stat_id": getattr(stat, 'stat_id', 0),
                        "enabled": getattr(stat, 'enabled', False),
                        "name": str(getattr(stat, 'name', 'Unknown')),
                        "display_name": str(getattr(stat, 'display_name', 'Unknown')),
                        "sort_order": getattr(stat, 'sort_order', 0),
                        "position_type": str(getattr(stat, 'position_type', 'Unknown')),
                        "is_only_display_stat": getattr(stat, 'is_only_display_stat', False)
                    }
                    stat_categories.append(stat_data)
                result["stat_categories"] = stat_categories

            # Add stat modifiers if available
            if hasattr(settings, 'stat_modifiers') and settings.stat_modifiers:
                stat_modifiers = []
                for modifier in settings.stat_modifiers:
                    modifier_data = {
                        "stat_id": getattr(modifier, 'stat_id', 0),
                        "value": getattr(modifier, 'value', 0)
                    }
                    stat_modifiers.append(modifier_data)
                result["stat_modifiers"] = stat_modifiers

            # Cache the result
            ttl = -1 if season else 300  # Historical data permanent, current data 5 min
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting league settings: {e}")
            return {"error": str(e)}

    # Register historical analysis tools
    register_historical_tools(mcp, app_state)

    # Register analytics tools
    register_analytics_tools(mcp, app_state)

