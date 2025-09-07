"""
Advanced Analytics and Pattern Recognition Tools for League Analysis MCP Server
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict, Set
from collections import defaultdict, Counter
import statistics

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class DraftStrategyData(TypedDict):
    """Type definition for draft strategy tracking structure."""
    position_preferences: Dict[str, List[int]]
    round_strategies: Dict[int, List[str]]
    auction_spending: List[Dict[str, Any]]
    early_round_positions: List[str]
    late_round_positions: List[str]
    total_drafts: int


class ManagerMetricsData(TypedDict):
    """Type definition for manager performance tracking structure."""
    wins: List[int]
    points_for: List[float]
    points_against: List[float]
    ranks: List[int]
    playoff_appearances: int
    championships: int
    seasons_played: int


class ComponentScores(TypedDict):
    """Type definition for skill component scores."""
    win_rate: float
    playoff_rate: float
    championship_rate: float
    consistency: float


class PerformanceMetrics(TypedDict):
    """Type definition for performance metrics."""
    avg_wins: float
    avg_points: float
    avg_rank: float
    championships: int
    playoff_appearances: int


class SkillEvaluation(TypedDict):
    """Type definition for skill evaluation results."""
    team_id: str
    seasons_analyzed: int
    overall_skill_score: float
    skill_tier: str
    component_scores: ComponentScores
    performance_metrics: PerformanceMetrics
    strengths: List[str]
    areas_for_improvement: List[str]


class TradePair(TypedDict):
    """Type definition for trade pair analysis."""
    team1_id: str
    team2_id: str
    total_trades: int
    trades_per_season: float
    likelihood_score: float


# Private functions for testing - extract core logic from MCP tools
def _analyze_draft_strategy_impl(league_id: str, sport: str, seasons: Optional[List[str]], 
                                team_id: Optional[str], app_state: Dict[str, Any]) -> Dict[str, Any]:
    """Core implementation of draft strategy analysis."""
    try:
        cache_manager = app_state["cache_manager"]
        game_ids = app_state["game_ids"]

        if not seasons:
            available_seasons = list(game_ids.get(sport, {}).keys())
            seasons = sorted(available_seasons, reverse=True)[:3]

        draft_strategies: Dict[str, DraftStrategyData] = defaultdict(lambda: {
            "position_preferences": {},
            "round_strategies": {},
            "auction_spending": [],
            "early_round_positions": [],
            "late_round_positions": [],
            "total_drafts": 0
        })

        for season in seasons:
            # Get cached draft data
            cached_draft = cache_manager.get_historical_data(
                sport, season, league_id, "draft_results"
            )

            if not cached_draft:
                continue

            draft_picks = cached_draft.get("draft_picks", [])
            is_auction = cached_draft.get("is_auction", False)

            for pick in draft_picks:
                tid = pick.get("team_id", "Unknown")
                if team_id and tid != team_id:
                    continue

                position = pick.get("position", "Unknown")
                round_num = pick.get("round", 0)
                cost = pick.get("cost", 0)

                team_data = draft_strategies[tid]
                team_data["total_drafts"] = team_data.get("total_drafts", 0) + 1
                
                pos_prefs = team_data["position_preferences"]
                if position not in pos_prefs:
                    pos_prefs[position] = []
                pos_prefs[position].append(round_num)
                
                round_strats = team_data["round_strategies"]
                if round_num not in round_strats:
                    round_strats[round_num] = []
                round_strats[round_num].append(position)

                if is_auction and cost > 0:
                    auction_spending = team_data["auction_spending"]
                    auction_spending.append({
                        "player": pick.get("player_name", "Unknown"),
                        "position": position,
                        "cost": cost
                    })

                # Categorize early vs late round preferences
                if round_num <= 3:
                    early_pos = team_data["early_round_positions"]
                    early_pos.append(position)
                elif round_num >= 10:
                    late_pos = team_data["late_round_positions"]
                    late_pos.append(position)

        # Analyze patterns
        strategy_analysis = {}
        for tid, data in draft_strategies.items():
            if data["total_drafts"] == 0:
                continue

            # Position preference analysis
            position_stats = {}
            pos_prefs = data.get("position_preferences", {})
            for pos, rounds in pos_prefs.items():
                if rounds:  # Only process if there are rounds
                    position_stats[pos] = {
                        "times_drafted": len(rounds),
                        "avg_round": statistics.mean(rounds),
                        "earliest_round": min(rounds),
                        "latest_round": max(rounds)
                    }

            # Early round strategy
            early_pos_list = data.get("early_round_positions", [])
            late_pos_list = data.get("late_round_positions", [])
            early_positions = Counter(early_pos_list)
            late_positions = Counter(late_pos_list)

            # Draft philosophy classification
            rb_early = early_positions.get("RB", 0)
            wr_early = early_positions.get("WR", 0)

            if rb_early > wr_early * 1.5:
                strategy_type = "RB-Heavy"
            elif wr_early > rb_early * 1.5:
                strategy_type = "Zero-RB"
            else:
                strategy_type = "Balanced"

            strategy_analysis[tid] = {
                "team_id": tid,
                "seasons_analyzed": len(
                    [
                        s for s in seasons if any(
                            p.get("team_id") == tid for s_data in [
                                cache_manager.get_historical_data(
                                    sport,
                                    s,
                                    league_id,
                                    "draft_results")] if s_data for p in s_data.get(
                                "draft_picks",
                                []))]),
                "total_picks_analyzed": data.get("total_drafts", 0),
                "position_preferences": position_stats,
                "early_round_focus": dict(
                    early_positions.most_common(3)),
                "late_round_focus": dict(
                    late_positions.most_common(3)),
                "draft_strategy_type": strategy_type,
                "auction_data": {
                    "total_auction_picks": len(auction_data) if (auction_data := data.get("auction_spending", [])) else 0,
                    "avg_cost_per_pick": statistics.mean(
                        [
                            p["cost"] for p in auction_data]) if auction_data and isinstance(auction_data, list) else 0,
                    "highest_cost_pick": max(
                        auction_data,
                        key=lambda x: x.get("cost", 0)) if auction_data and isinstance(auction_data, list) else None
                } if data.get("auction_spending") else None}

        return {
            "league_id": league_id,
            "sport": sport,
            "seasons_analyzed": seasons,
            "team_filter": team_id,
            "draft_strategies": strategy_analysis,
            "total_teams_analyzed": len(strategy_analysis)
        }

    except Exception as e:
        logger.error(f"Error analyzing draft strategy: {e}")
        return {"error": str(e)}


def _predict_trade_likelihood_impl(league_id: str, sport: str, team1_id: Optional[str], 
                                  team2_id: Optional[str], seasons: Optional[List[str]], 
                                  app_state: Dict[str, Any]) -> Dict[str, Any]:
    """Core implementation of trade likelihood prediction."""
    try:
        cache_manager = app_state["cache_manager"]
        game_ids = app_state["game_ids"]

        if not seasons:
            available_seasons = list(game_ids.get(sport, {}).keys())
            seasons = sorted(available_seasons, reverse=True)[:3]

        trade_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        trade_details: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for season in seasons:
            # Get cached transaction data
            cached_transactions = cache_manager.get_historical_data(
                sport, season, league_id, "transactions"
            )

            if not cached_transactions:
                continue

            transactions = cached_transactions.get("transactions", [])

            for transaction in transactions:
                if transaction.get("type") != "trade":
                    continue

                # Extract team IDs from trade (simplified - would need more complex parsing in reality)
                players = transaction.get("players", [])
                if len(players) >= 2:
                    # Extract team IDs from transaction players
                    trade_teams: Set[str] = set()
                    for player in players:
                        # Extract team info from player transaction data
                        if isinstance(player, dict):
                            # Try multiple possible team ID locations in YFPY data
                            team_id = (player.get("team_id") or 
                                     player.get("editorial_team_id") or
                                     player.get("selected_position", {}).get("team_id"))
                            if team_id:
                                trade_teams.add(str(team_id))
                        elif hasattr(player, 'team_id'):
                            trade_teams.add(str(player.team_id))
                        elif hasattr(player, 'editorial_team_id'):
                            trade_teams.add(str(player.editorial_team_id))

                    if len(trade_teams) == 2:
                        t1, t2 = list(trade_teams)
                        trade_matrix[t1][t2] += 1
                        trade_matrix[t2][t1] += 1
                        trade_details[f"{t1}-{t2}"].append({
                            "season": season,
                            "players": [p.get("name", "Unknown") for p in players],
                            "timestamp": transaction.get("timestamp")
                        })

        # Calculate trade probabilities
        if team1_id and team2_id:
            # Specific pair analysis
            trades_between = trade_matrix[team1_id][team2_id]
            total_seasons = len(seasons)

            prediction = {
                "team1_id": team1_id,
                "team2_id": team2_id,
                "historical_trades": trades_between,
                "seasons_analyzed": total_seasons,
                "trades_per_season": trades_between / total_seasons if total_seasons > 0 else 0,
                "likelihood_score": min(trades_between / max(total_seasons, 1), 1.0),
                "trade_history": trade_details.get(f"{team1_id}-{team2_id}", []),
                "recommendation": "High" if trades_between >= 2 else "Medium" if trades_between >= 1 else "Low"
            }
        else:
            # League-wide analysis
            all_trade_pairs: Dict[str, TradePair] = {}
            for t1, partners in trade_matrix.items():
                for t2, count in partners.items():
                    if t1 < t2:  # Avoid duplicates
                        pair_key = f"{t1}-{t2}"
                        all_trade_pairs[pair_key] = {
                            "team1_id": t1,
                            "team2_id": t2,
                            "total_trades": count,
                            "trades_per_season": count / len(seasons) if seasons else 0,
                            "likelihood_score": min(count / max(len(seasons), 1), 1.0)
                        }

            prediction = {
                "league_id": league_id,
                "sport": sport,
                "seasons_analyzed": seasons,
                "all_trade_pairs": all_trade_pairs,
                "most_active_pairs": sorted(
                    all_trade_pairs.items(),
                    key=lambda x: int(x[1]["total_trades"]), 
                    reverse=True
                )[:5],
                "total_unique_pairs": len(all_trade_pairs)
            }

        return prediction

    except Exception as e:
        logger.error(f"Error predicting trade likelihood: {e}")
        return {"error": str(e)}


def _evaluate_manager_skill_impl(league_id: str, sport: str, seasons: Optional[List[str]], 
                                team_id: Optional[str], app_state: Dict[str, Any]) -> Dict[str, Any]:
    """Core implementation of manager skill evaluation."""
    try:
        cache_manager = app_state["cache_manager"]
        game_ids = app_state["game_ids"]

        if not seasons:
            available_seasons = list(game_ids.get(sport, {}).keys())
            seasons = sorted(available_seasons, reverse=True)[:3]

        manager_metrics: Dict[str, ManagerMetricsData] = defaultdict(lambda: {
            "wins": [],
            "points_for": [],
            "points_against": [],
            "ranks": [],
            "playoff_appearances": 0,
            "championships": 0,
            "seasons_played": 0
        })

        # Collect performance data
        for season in seasons:
            cached_standings = cache_manager.get_historical_data(
                sport, season, league_id, "standings"
            )

            if not cached_standings:
                continue

            teams = cached_standings.get("teams", [])
            for team in teams:
                tid = team.get("team_id")
                if team_id and tid != team_id:
                    continue

                team_metrics = manager_metrics[tid]
                
                wins_list = team_metrics["wins"]
                wins_list.append(team.get("wins", 0))
                
                pf_list = team_metrics["points_for"]
                pf_list.append(float(team.get("points_for", 0)))
                
                pa_list = team_metrics["points_against"]
                pa_list.append(float(team.get("points_against", 0)))
                
                ranks_list = team_metrics["ranks"]
                ranks_list.append(team.get("rank", 999))
                
                team_metrics["seasons_played"] = team_metrics.get("seasons_played", 0) + 1

                if team.get("rank", 999) == 1:
                    team_metrics["championships"] = team_metrics.get("championships", 0) + 1
                if team.get("rank", 999) <= 6:  # Assuming 6 playoff teams
                    team_metrics["playoff_appearances"] = team_metrics.get("playoff_appearances", 0) + 1

        # Calculate skill scores
        skill_evaluations: Dict[str, SkillEvaluation] = {}
        for tid, metrics in manager_metrics.items():
            seasons_played = metrics.get("seasons_played", 0)
            if seasons_played == 0:
                continue

            wins = metrics.get("wins", [])
            points_for = metrics.get("points_for", [])
            ranks = metrics.get("ranks", [])

            # Core metrics
            avg_wins = statistics.mean(wins) if wins else 0
            avg_points = statistics.mean(points_for) if points_for else 0
            avg_rank = statistics.mean(ranks) if ranks else 0

            # Advanced metrics
            win_consistency = (
                1 - (statistics.stdev(wins) / avg_wins) 
                if avg_wins > 0 and len(wins) > 1 else 0
            )
            scoring_consistency = (
                1 - (statistics.stdev(points_for) / avg_points)
                if avg_points > 0 and len(points_for) > 1 else 0
            )
            rank_consistency = (
                1 - (statistics.stdev(ranks) / avg_rank) 
                if avg_rank > 0 and len(ranks) > 1 else 0
            )

            # Skill components (0-100 scale)
            win_rate_score = min((avg_wins / 13) * 100, 100) if avg_wins > 0 else 0  # Assuming ~13 games per season
            
            playoff_apps = metrics.get("playoff_appearances", 0)
            championships = metrics.get("championships", 0)
            playoff_rate_score = (playoff_apps / seasons_played) * 100 if seasons_played > 0 else 0
            championship_rate_score = (championships / seasons_played) * 100 if seasons_played > 0 else 0
            consistency_score = (win_consistency + scoring_consistency + rank_consistency) / 3 * 100

            # Overall skill score (weighted average)
            overall_skill = (
                win_rate_score * 0.3
                + playoff_rate_score * 0.25
                + championship_rate_score * 0.25
                + consistency_score * 0.2
            )

            # Skill tier classification
            if overall_skill >= 80:
                skill_tier = "Elite"
            elif overall_skill >= 65:
                skill_tier = "Above Average"
            elif overall_skill >= 50:
                skill_tier = "Average"
            elif overall_skill >= 35:
                skill_tier = "Below Average"
            else:
                skill_tier = "Needs Improvement"

            skill_evaluations[tid] = {
                "team_id": tid,
                "seasons_analyzed": seasons_played,
                "overall_skill_score": round(overall_skill, 2),
                "skill_tier": skill_tier,
                "component_scores": {
                    "win_rate": round(win_rate_score, 2),
                    "playoff_rate": round(playoff_rate_score, 2),
                    "championship_rate": round(championship_rate_score, 2),
                    "consistency": round(consistency_score, 2)
                },
                "performance_metrics": {
                    "avg_wins": round(avg_wins, 2),
                    "avg_points": round(avg_points, 2),
                    "avg_rank": round(avg_rank, 2),
                    "championships": metrics["championships"],
                    "playoff_appearances": metrics["playoff_appearances"]
                },
                "strengths": [],
                "areas_for_improvement": []
            }

            # Identify strengths and weaknesses
            scores = skill_evaluations[tid]["component_scores"]
            if scores["win_rate"] >= 70:
                skill_evaluations[tid]["strengths"].append("Consistent regular season performance")
            if scores["playoff_rate"] >= 75:
                skill_evaluations[tid]["strengths"].append("Strong playoff qualifier")
            if scores["championship_rate"] >= 33:
                skill_evaluations[tid]["strengths"].append("Championship-level manager")
            if scores["consistency"] >= 70:
                skill_evaluations[tid]["strengths"].append("Very consistent performance")

            if scores["win_rate"] < 40:
                skill_evaluations[tid]["areas_for_improvement"].append("Regular season record")
            if scores["playoff_rate"] < 50:
                skill_evaluations[tid]["areas_for_improvement"].append("Playoff qualification")
            if scores["consistency"] < 40:
                skill_evaluations[tid]["areas_for_improvement"].append("Performance consistency")

        return {
            "league_id": league_id,
            "sport": sport,
            "seasons_analyzed": seasons,
            "team_filter": team_id,
            "skill_evaluations": skill_evaluations,
            "league_average_skill": (
                statistics.mean([e["overall_skill_score"] for e in skill_evaluations.values()])
                if skill_evaluations else 0.0
            ),
            "total_managers_evaluated": len(skill_evaluations)
        }

    except Exception as e:
        logger.error(f"Error evaluating manager skill: {e}")
        return {"error": str(e)}


# Public API functions for direct import (used by tests)
def analyze_draft_strategy(league_id: str, sport: str = "nfl",
                          seasons: Optional[List[str]] = None,
                          team_id: Optional[str] = None,
                          app_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze draft strategies and identify manager tendencies.

    Args:
        league_id: Yahoo league ID
        sport: Sport code (nfl, nba, mlb, nhl)
        seasons: List of seasons to analyze (default: last 3 years)
        team_id: Specific team to analyze (optional)
        app_state: App state containing cache and game IDs (required for standalone use)

    Returns:
        Draft strategy analysis and patterns
    """
    # Import here to avoid circular imports
    from .server import app_state as default_app_state
    
    # Use provided app_state or default from server
    if app_state is None:
        app_state = default_app_state
        
    if not app_state:
        raise ValueError("App state not available - server not initialized")
        
    return _analyze_draft_strategy_impl(league_id, sport, seasons, team_id, app_state)


def predict_trade_likelihood(league_id: str, sport: str = "nfl",
                             team1_id: Optional[str] = None, team2_id: Optional[str] = None,
                             seasons: Optional[List[str]] = None,
                             app_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Predict trade likelihood between managers based on historical patterns.

    Args:
        league_id: Yahoo league ID
        sport: Sport code (nfl, nba, mlb, nhl)
        team1_id: First team ID (optional)
        team2_id: Second team ID (optional)
        seasons: Seasons to analyze for patterns (default: last 3 years)
        app_state: App state containing cache and game IDs (required for standalone use)

    Returns:
        Trade likelihood predictions and historical trade patterns
    """
    # Import here to avoid circular imports
    from .server import app_state as default_app_state
    
    # Use provided app_state or default from server
    if app_state is None:
        app_state = default_app_state
        
    if not app_state:
        raise ValueError("App state not available - server not initialized")
        
    return _predict_trade_likelihood_impl(league_id, sport, team1_id, team2_id, seasons, app_state)


def evaluate_manager_skill(league_id: str, sport: str = "nfl",
                          seasons: Optional[List[str]] = None,
                          team_id: Optional[str] = None,
                          app_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate manager skill based on multiple performance metrics.

    Args:
        league_id: Yahoo league ID
        sport: Sport code (nfl, nba, mlb, nhl)
        seasons: Seasons to analyze (default: last 3 years)
        team_id: Specific team to evaluate (optional)
        app_state: App state containing cache and game IDs (required for standalone use)

    Returns:
        Comprehensive manager skill evaluation
    """
    # Import here to avoid circular imports
    from .server import app_state as default_app_state
    
    # Use provided app_state or default from server
    if app_state is None:
        app_state = default_app_state
        
    if not app_state:
        raise ValueError("App state not available - server not initialized")
        
    return _evaluate_manager_skill_impl(league_id, sport, seasons, team_id, app_state)


def register_analytics_tools(mcp: FastMCP, app_state: Dict[str, Any]) -> None:
    """Register advanced analytics and pattern recognition tools."""

    @mcp.tool()
    def analyze_draft_strategy_tool(league_id: str, sport: str = "nfl",
                                   seasons: Optional[List[str]] = None,
                                   team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze draft strategies and identify manager tendencies.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: List of seasons to analyze (default: last 3 years)
            team_id: Specific team to analyze (optional)

        Returns:
            Draft strategy analysis and patterns
        """
        return _analyze_draft_strategy_impl(league_id, sport, seasons, team_id, app_state)

    @mcp.tool()
    def predict_trade_likelihood_tool(league_id: str, sport: str = "nfl",
                                     team1_id: Optional[str] = None, team2_id: Optional[str] = None,
                                     seasons: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Predict trade likelihood between managers based on historical patterns.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            team1_id: First team ID (optional)
            team2_id: Second team ID (optional)
            seasons: Seasons to analyze for patterns (default: last 3 years)

        Returns:
            Trade likelihood predictions and historical trade patterns
        """
        return _predict_trade_likelihood_impl(league_id, sport, team1_id, team2_id, seasons, app_state)

    @mcp.tool()
    def evaluate_manager_skill_tool(league_id: str, sport: str = "nfl",
                                   seasons: Optional[List[str]] = None,
                                   team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate manager skill based on multiple performance metrics.

        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: Seasons to analyze (default: last 3 years)
            team_id: Specific team to evaluate (optional)

        Returns:
            Comprehensive manager skill evaluation
        """
        return _evaluate_manager_skill_impl(league_id, sport, seasons, team_id, app_state)
