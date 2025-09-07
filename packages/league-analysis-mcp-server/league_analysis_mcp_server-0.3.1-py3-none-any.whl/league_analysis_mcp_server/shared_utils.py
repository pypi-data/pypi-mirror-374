"""
Shared utility functions for League Analysis MCP Server.

This module contains common functionality used across multiple tool modules
to eliminate code duplication and ensure consistency.
"""

import logging
from typing import Any, Dict, Optional
from yfpy import YahooFantasySportsQuery

logger = logging.getLogger(__name__)


def get_yahoo_query(league_id: str, app_state: Dict, game_id: Optional[str] = None, sport: str = "nfl") -> YahooFantasySportsQuery:
    """
    Create a Yahoo Fantasy Sports Query object for API calls.
    
    Centralized function to eliminate duplication across tool modules.
    
    Args:
        league_id: Yahoo league ID
        app_state: Application state containing auth manager and game IDs
        game_id: Specific game ID (optional, will be resolved from sport/season)
        sport: Sport code (nfl, nba, mlb, nhl)
        
    Returns:
        Configured YahooFantasySportsQuery object
        
    Raises:
        Exception: If authentication fails or game_id cannot be resolved
    """
    try:
        auth_manager = app_state.get("auth_manager")
        if not auth_manager:
            raise Exception("Authentication manager not found in app_state")
        
        credentials = auth_manager.get_yahoo_credentials()
        if not credentials:
            raise Exception("Yahoo credentials not available")
            
        # Resolve game_id if not provided
        if not game_id:
            game_ids = app_state.get("game_ids", {})
            if sport in game_ids:
                # Use current season's game ID
                current_games = game_ids[sport]
                if current_games:
                    # Get the most recent game ID (highest year)
                    latest_year = max(current_games.keys())
                    game_id = current_games[latest_year]
                else:
                    raise Exception(f"No game IDs available for sport: {sport}")
            else:
                raise Exception(f"Sport not supported: {sport}")
        
        # Create query object
        yahoo_query = YahooFantasySportsQuery(
            league_id=league_id,
            game_id=game_id,
            consumer_key=credentials["consumer_key"],
            consumer_secret=credentials["consumer_secret"],
            access_token=credentials.get("access_token"),
            access_token_secret=credentials.get("access_token_secret"),
            refresh_token=credentials.get("refresh_token")
        )
        
        logger.debug(f"Created Yahoo query for league {league_id}, sport {sport}, game_id {game_id}")
        return yahoo_query
        
    except Exception as e:
        logger.error(f"Failed to create Yahoo query: {e}")
        raise


def standardize_cache_key(category: str, identifiers: Dict[str, Any], season: Optional[str] = None) -> str:
    """
    Generate standardized cache keys across all modules.
    
    Args:
        category: Cache category (e.g., "league_info", "standings", "roster")
        identifiers: Dictionary of identifying parameters
        season: Season year (optional)
        
    Returns:
        Standardized cache key string
    """
    key_parts = [category]
    
    # Add identifiers in consistent order
    for key in sorted(identifiers.keys()):
        value = identifiers[key]
        if value is not None:
            key_parts.append(f"{key}:{value}")
    
    # Add season if provided
    if season:
        key_parts.append(f"season:{season}")
    
    return "/".join(key_parts)


def handle_api_error(operation: str, error: Exception) -> Dict[str, Any]:
    """
    Standardized API error handling across all modules.
    
    Args:
        operation: Description of the operation that failed
        error: The exception that occurred
        
    Returns:
        Standardized error response dictionary
    """
    error_message = str(error)
    logger.error(f"Error in {operation}: {error_message}")
    
    # Categorize common error types
    if "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
        return {
            "error": f"Authentication required for {operation}. Please check your Yahoo credentials.",
            "error_type": "authentication",
            "operation": operation
        }
    elif "rate limit" in error_message.lower() or "too many requests" in error_message.lower():
        return {
            "error": f"Rate limit exceeded for {operation}. Please try again later.",
            "error_type": "rate_limit", 
            "operation": operation
        }
    elif "timeout" in error_message.lower():
        return {
            "error": f"Request timeout for {operation}. Yahoo API may be experiencing issues.",
            "error_type": "timeout",
            "operation": operation
        }
    else:
        return {
            "error": f"Error in {operation}: {error_message}",
            "error_type": "general",
            "operation": operation
        }