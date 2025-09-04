# League Analysis MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI assistants with access to Yahoo Fantasy Sports data, including advanced historical analysis and manager profiling capabilities.

## Features

### 🏈 Multi-Sport Support
- **NFL** (National Football League)
- **NBA** (National Basketball Association) 
- **MLB** (Major League Baseball)
- **NHL** (National Hockey League)

### 📊 Current Season Data
- League information and settings
- Real-time standings
- Team rosters and lineups
- Weekly matchups and scoring
- Transaction history

### 📈 Historical Analysis
- **Multi-season draft analysis** - Track draft patterns and strategies over time
- **Manager performance history** - Comprehensive performance metrics across seasons
- **Transaction pattern analysis** - Trading behavior and partnership identification
- **Season-to-season comparisons** - League evolution and competitive balance trends

### 🧠 Advanced Analytics
- **Draft strategy classification** - Identify RB-heavy, Zero-RB, or balanced approaches
- **Manager skill evaluation** - Comprehensive skill scoring based on multiple metrics
- **Trade likelihood prediction** - Predict trade partnerships based on historical patterns
- **Pattern recognition** - Identify trends in manager behavior and league dynamics

### ⚡ Performance Features
- **Smart caching** - Historical data cached permanently, current data with TTL
- **Rate limiting** - Respects Yahoo API limits
- **Error handling** - Comprehensive error handling and logging
- **Multi-season support** - Access data from 2015+ seasons

## Installation

### Prerequisites
- **Python 3.10+**
- **uv installed** (Python package manager)
- Yahoo Developer App credentials (setup will guide you)

### 🚀 Install uv (Required)

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### ✨ No Package Installation Required!

The server **automatically downloads** when you configure your MCP client. Just add the configuration below - no separate package installation needed!

**How it works:**
1. You install `uv` (the package manager)
2. You configure your MCP client to use `uvx league-analysis-mcp-server`
3. When your MCP client starts, `uvx` automatically downloads the server from PyPI
4. Subsequent starts use the cached version

### 🔧 Development Installation

**From Source:**
```bash
git clone https://github.com/ari1110/League-Analysis-MCP.git
cd League-Analysis-MCP
uv sync --all-extras
```

Then set up authentication using the conversational MCP tools (see streamlined setup below).

## 🚀 **NEW! Streamlined Authentication Setup**

**No more complex setup scripts!** Authentication is now handled entirely through conversational MCP tools with **two OAuth options**:

### **Option 1: Automated OAuth (Recommended)**

**5-Step Setup Process:**
1. **Install & Connect** - Add server to your MCP client
2. **Check Status** - AI assistant runs `check_setup_status()` 
3. **Create Yahoo App** - AI assistant shows you exactly what to do with `create_yahoo_app()`
4. **Save Credentials** - AI assistant saves them for you with `save_yahoo_credentials(key, secret)`
5. **Automated OAuth** - AI assistant runs `start_automated_oauth_flow()` for fully automated setup

**✨ Fully Automated Experience:**
- Browser opens automatically to Yahoo authorization page
- You sign in and authorize the app  
- HTTPS callback server automatically captures the authorization code
- Tokens are saved and exchanged automatically
- Success page displays and auto-closes
- **Total time: ~30 seconds!**

### **Option 2: Manual OAuth (Fallback)**

**5-Step Setup Process:**
1. **Install & Connect** - Add server to your MCP client
2. **Check Status** - AI assistant runs `check_setup_status()` 
3. **Create Yahoo App** - AI assistant shows you exactly what to do with `create_yahoo_app()`
4. **Save Credentials** - AI assistant saves them for you with `save_yahoo_credentials(key, secret)`
5. **Manual OAuth** - AI assistant guides you through `start_oauth_flow()` and `complete_oauth_flow(code)`

**📋 Manual Code Entry:**
- AI provides authorization URL
- You visit URL, sign in, and get verification code
- You provide the code to the AI assistant
- AI completes token exchange

**That's it!** ✨ Everything happens in your conversation with the AI assistant. No file editing, no command line scripts, no leaving the interface.

### **🔑 Important OAuth Requirements**

**For Best Results:**
- **✅ Sign into Yahoo first**: Before starting OAuth, sign into [yahoo.com](https://yahoo.com) in your browser
- **✅ Use the same account**: Sign in with the Yahoo account that has your fantasy leagues  
- **✅ Stay signed in**: Keep your Yahoo session active during the OAuth process

**Why this matters:**
- **Automated OAuth works best** when you're already signed into Yahoo
- **Fresh logins during OAuth** can sometimes cause Yahoo's "uh-oh" errors
- **Existing sessions** provide the smoothest authorization experience

**SSL Certificate Handling:**
When using automated OAuth, your browser may show a security warning for `https://localhost:8080`. This is normal and safe:
1. Click **"Advanced"** or **"Show Details"**
2. Click **"Proceed to localhost (unsafe)"** or similar
3. The success page will display and auto-close after 3 seconds

**Troubleshooting:**
- **"uh-oh" errors**: Try signing into Yahoo first, then retry the OAuth flow
- **SSL warnings**: These are normal for self-signed certificates - safe to proceed
- **Timeouts**: Use manual OAuth flow as fallback if automated flow has issues

### **Example User Experience:**

```
You: "Show me my fantasy league standings"

AI: Let me check that for you. First, I need to check your authentication setup.
    → Runs check_setup_status()
    
AI: I see you need to create a Yahoo Developer app first. Here are the exact steps:
    → Runs create_yahoo_app()
    → Shows step-by-step instructions with exact values to use

You: "I created the app! My key is dj0yJmk9... and secret is abc123..."

AI: Perfect! Let me save those credentials for you.
    → Runs save_yahoo_credentials(key, secret)
    → Automatically saves to your environment

AI: Great! Now let's complete the OAuth authorization. Please visit this URL:
    → Runs start_oauth_flow()
    → Shows authorization URL and clear instructions

You: "I authorized it and got code: xyz789"

AI: Excellent! Let me complete the setup.
    → Runs complete_oauth_flow("xyz789")
    
AI: 🎉 Setup complete! Now let me get your league standings...
    → Runs get_standings() and shows your data
```

**Total time: ~2 minutes.** No technical knowledge required!

### 🔧 **Development Setup (Advanced Users)**

For development or troubleshooting, you can also run the server manually after installing dependencies with `uv sync --all-extras`.

## Usage

### Starting the Server
```bash
# PyPI Installation (recommended):
uvx league-analysis-mcp-server

# Or if installed with pip:
league-analysis-mcp-server

# Development/Source:
uv run python -m src.server
```

## 🔌 MCP Client Configuration

**For detailed setup instructions for all MCP clients, see [MCP_INTEGRATION_GUIDE.md](MCP_INTEGRATION_GUIDE.md)**

**Quick setup for Claude Desktop:**
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "league-analysis": {
      "command": "uvx",
      "args": ["league-analysis-mcp-server"]
    }
  }
}
```

The integration guide covers configuration for Claude Desktop, Claude Code, Continue.dev, and other MCP clients with complete examples and troubleshooting.

### 🔧 Testing Your Connection

After adding to your MCP client:

1. **Restart your MCP client** (Claude Desktop, etc.)
2. **Test the connection** by asking:
   - "Can you get server info for the league analysis server?"
   - "List available seasons for NFL"
   - "What fantasy sports tools are available?"
3. **Check server status** with: `get_server_info()`

### 🚨 Troubleshooting MCP Connection

**Common issues:**

1. **Server not found:**
   - Check the file path in your config
   - Ensure UV is installed and in PATH
   - Verify the server starts manually: `uv run python -m src.server`

2. **Authentication errors:**
   - Use the streamlined setup: Ask your AI assistant to run `check_setup_status()`
   - Follow the conversational setup process using MCP tools
   - Check your Yahoo Developer app settings (redirect URI must be `https://localhost:8080/`)

3. **Permission issues:**
   - Ensure your MCP client has permission to execute UV
   - Check working directory permissions

4. **Environment variables:**
   - MCP clients may not inherit your shell environment
   - Create `.env` file in project root with credentials

### Available Tools

#### **🔐 Streamlined Authentication Tools** ✨ **NEW!**
- `check_setup_status()` - Check current authentication state and get next steps
- `create_yahoo_app()` - Step-by-step Yahoo Developer app creation guide
- `save_yahoo_credentials(consumer_key, consumer_secret)` - Save Yahoo app credentials
- **`start_automated_oauth_flow()` - 🚀 Fully automated OAuth with callback server (recommended)**
- `start_oauth_flow()` - Begin manual OAuth authorization with clear instructions  
- `complete_oauth_flow(verification_code)` - Complete manual setup with verification code
- `test_yahoo_connection()` - Test API connectivity and troubleshoot issues
- `reset_authentication()` - Clear all auth data to start fresh

#### Basic League Tools
- `get_server_info()` - Server status and configuration
- `get_setup_instructions()` - Comprehensive setup help (includes new tools guidance)
- `list_available_seasons(sport)` - Available historical seasons
- `get_league_info(league_id, sport, season?)` - League settings and metadata
- `get_standings(league_id, sport, season?)` - Current or historical standings
- `get_team_roster(league_id, team_id, sport, season?)` - Team roster information
- `get_matchups(league_id, sport, week?, season?)` - Weekly matchup data

#### Historical Analysis Tools
- `get_historical_drafts(league_id, sport, seasons?)` - Draft results across seasons
- `get_season_transactions(league_id, sport, season)` - Transaction history for season
- `analyze_manager_history(league_id, sport, seasons?, team_id?)` - Manager performance patterns
- `compare_seasons(league_id, sport, seasons)` - Season-to-season analysis

#### Advanced Analytics Tools
- `analyze_draft_strategy(league_id, sport, seasons?, team_id?)` - Draft pattern analysis
- `predict_trade_likelihood(league_id, sport, team1_id?, team2_id?, seasons?)` - Trade predictions
- `evaluate_manager_skill(league_id, sport, seasons?, team_id?)` - Comprehensive skill evaluation

#### Cache Management
- `clear_cache(cache_type?)` - Clear cached data ('all', 'current', 'historical')

### Available Resources

Access read-only data through these resource URIs:

- `league_overview://sport/league_id[/season]` - Comprehensive league overview
- `current_week://sport/league_id` - Current week activity and focus areas
- `league_history://sport/league_id` - Multi-season history and trends
- `manager_profiles://sport/league_id[/team_id]` - Manager profiling information

## Example Usage

```python
# Get basic league info
result = get_league_info("123456", "nfl")

# Analyze manager performance across last 3 seasons  
analysis = analyze_manager_history("123456", "nfl", ["2022", "2023", "2024"])

# Get draft strategies for all managers
draft_analysis = analyze_draft_strategy("123456", "nfl", ["2022", "2023", "2024"])

# Evaluate manager skill levels
skill_eval = evaluate_manager_skill("123456", "nfl", ["2022", "2023", "2024"])

# Predict trade likelihood between specific managers
trade_pred = predict_trade_likelihood("123456", "nfl", "team1", "team2")
```

## Configuration

### Game IDs
The server includes game ID mappings for seasons 2015-2024 across all supported sports. These are automatically used when specifying historical seasons.

### Caching Strategy
- **Historical data**: Cached permanently (TTL = -1)
- **Current season data**: Cached for 5 minutes (TTL = 300)
- **Cache size**: Limited to 100MB by default

### Rate Limiting
- **Default**: 60 requests per minute
- **Burst limit**: 10 requests
- Automatically handled by the server

## Architecture

### Core Components
- **FastMCP 2.0**: High-level MCP framework for rapid development
- **YFPY**: Yahoo Fantasy Sports API wrapper
- **Caching Layer**: Smart caching for performance optimization
- **Authentication Manager**: OAuth handling for Yahoo API access
- **Analytics Engine**: Advanced pattern recognition and predictions

### Data Flow
1. **Request** → Authentication → Cache Check → Yahoo API → Response Processing → Cache Storage → **Response**
2. **Historical Data**: Cached permanently after first fetch
3. **Current Data**: Cached with TTL, automatically refreshed

### Error Handling
- Comprehensive error logging
- Graceful degradation for missing data
- Cache fallback for API failures
- User-friendly error messages

## Supported Analysis Types

### Manager Profiling
- **Performance Tiers**: Elite, Above Average, Average, Below Average, Needs Improvement
- **Consistency Scoring**: Win rate, scoring, and ranking consistency
- **Success Patterns**: Championship rate, playoff appearances, trajectory analysis

### Draft Strategy Classification
- **RB-Heavy**: Prioritizes running backs in early rounds
- **Zero-RB**: Waits on running backs, focuses on WR/other positions
- **Balanced**: Even distribution across position types
- **Auction Analysis**: Spending patterns and value identification

### Trade Pattern Analysis
- **Partnership Identification**: Historical trade frequency between managers
- **Likelihood Scoring**: Probability of future trades based on history
- **Trade Timing**: Seasonal patterns and deadline behavior

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - **✅ NEW**: Use streamlined setup by asking AI to run `check_setup_status()`
   - **🚀 Recommended**: Try `start_automated_oauth_flow()` for easiest setup
   - **⚠️ "uh-oh" errors**: Sign into yahoo.com first, then retry OAuth
   - **🔄 Reset & retry**: Use `reset_authentication()` to start fresh
   - **🔧 Manual setup**: Verify Yahoo Consumer Key/Secret in .env
   - **📝 Help**: Run `get_setup_instructions()` for detailed guidance

2. **OAuth Troubleshooting**
   - **SSL certificate warnings**: Normal for automated OAuth - safe to proceed
   - **Timeout during OAuth**: Try manual OAuth as fallback (`start_oauth_flow()`)
   - **Yahoo session issues**: Sign into Yahoo first, keep session active
   - **Port conflicts**: Ensure nothing else uses port 8080
   - **Browser compatibility**: Modern browsers work best (Chrome, Edge, Firefox)

2. **No Historical Data**
   - Ensure league has existed for multiple seasons
   - Verify correct league ID and sport combination
   - Check game ID mappings in config/game_ids.json

3. **Cache Issues**
   - Use `clear_cache("all")` to reset all cached data
   - Check cache statistics with `get_server_info()`

4. **Rate Limiting**
   - Server automatically handles rate limits
   - Historical data queries may take longer due to multiple API calls
   - Use caching to minimize repeated requests

### Support

For issues and feature requests, please check the documentation or create an issue in the project repository.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read the contributing guidelines and submit pull requests for any improvements.