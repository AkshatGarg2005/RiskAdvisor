"""
Market Analyzer Agent using Google ADK with Google Search grounding.
Uses multi-agent architecture to combine google_search (built-in) with custom stock tools.

ADK Limitation: Built-in tools like google_search cannot be mixed with custom function tools 
in the same agent. Solution: Use AgentTool to delegate to specialized sub-agents.
"""
import os
import requests
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Mock prices fallback - ONLY used when Alpha Vantage is unavailable
MOCK_PRICES = {
    "AAPL": {"price": 195.50, "change": 2.30, "change_percent": "1.19%", "volume": 45000000},
    "GOOGL": {"price": 142.80, "change": -1.20, "change_percent": "-0.83%", "volume": 20000000},
    "MSFT": {"price": 378.90, "change": 4.50, "change_percent": "1.20%", "volume": 25000000},
    "AMZN": {"price": 178.25, "change": 3.10, "change_percent": "1.77%", "volume": 35000000},
    "TSLA": {"price": 248.50, "change": -5.80, "change_percent": "-2.28%", "volume": 80000000},
    "NVDA": {"price": 495.80, "change": 12.30, "change_percent": "2.54%", "volume": 50000000},
    "META": {"price": 325.40, "change": 6.20, "change_percent": "1.94%", "volume": 15000000},
    "SPY": {"price": 458.25, "change": 3.50, "change_percent": "0.77%", "volume": 70000000},
}


def get_live_stock_price(symbol: str) -> dict:
    """
    Fetch live stock price from Alpha Vantage API.
    Falls back to mock data ONLY if API is unavailable.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
        
    Returns:
        Dictionary with current price, change, percent change, volume, and data source
    """
    symbol = symbol.upper().strip()
    
    # Try Alpha Vantage first
    if ALPHA_VANTAGE_API_KEY:
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                price = float(quote.get("05. price", 0))
                change = float(quote.get("09. change", 0))
                change_pct = quote.get("10. change percent", "0%")
                volume = int(quote.get("06. volume", 0))
                
                return {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "change_percent": change_pct,
                    "volume": volume,
                    "data_source": "LIVE - Alpha Vantage",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                # API returned but no data (rate limit or invalid symbol)
                error_msg = data.get("Note", data.get("Information", "Unknown error"))
                print(f"⚠️ Alpha Vantage: {error_msg}")
                
        except Exception as e:
            print(f"⚠️ Alpha Vantage API error: {e}")
    
    # Fallback to mock data ONLY if API unavailable
    if symbol in MOCK_PRICES:
        mock = MOCK_PRICES[symbol]
        return {
            "symbol": symbol,
            "price": mock["price"],
            "change": mock["change"],
            "change_percent": mock["change_percent"],
            "volume": mock["volume"],
            "data_source": "DEMO DATA - API unavailable",
            "timestamp": datetime.now().isoformat(),
            "status": "fallback"
        }
    
    return {
        "symbol": symbol,
        "price": 0,
        "change": 0,
        "change_percent": "0%",
        "volume": 0,
        "data_source": "UNKNOWN",
        "timestamp": datetime.now().isoformat(),
        "status": "not_found",
        "error": f"Symbol {symbol} not found"
    }


def analyze_stock_trend(symbol: str, current_price: float, price_change: float, price_change_percent: str) -> dict:
    """
    Analyze stock trend based on current data and provide directional outlook.
    
    Args:
        symbol: Stock ticker symbol
        current_price: Current stock price
        price_change: Today's price change in dollars
        price_change_percent: Today's percentage change
        
    Returns:
        Dictionary with trend analysis and short-term outlook
    """
    symbol = symbol.upper()
    
    # Parse percent change
    try:
        pct = float(price_change_percent.replace("%", "").replace("+", ""))
    except:
        pct = 0
    
    # Determine momentum
    if pct > 2:
        momentum = "STRONG BULLISH"
        outlook = "positive"
    elif pct > 0.5:
        momentum = "BULLISH"
        outlook = "mildly positive"
    elif pct > -0.5:
        momentum = "NEUTRAL"
        outlook = "sideways"
    elif pct > -2:
        momentum = "BEARISH" 
        outlook = "mildly negative"
    else:
        momentum = "STRONG BEARISH"
        outlook = "negative"
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "today_change": price_change,
        "today_percent": price_change_percent,
        "momentum": momentum,
        "short_term_outlook": outlook,
        "analysis": f"{symbol} is showing {momentum} momentum with a {price_change_percent} move today. "
                   f"Current price: ${current_price:.2f}. Short-term outlook appears {outlook}.",
        "disclaimer": "This is analysis based on current data, not financial advice."
    }


# ============================================================================
# MULTI-AGENT ARCHITECTURE
# ============================================================================

# Agent 1: Search Agent - ONLY has google_search (built-in tool)
# This agent searches the web for market news, analyst opinions, forecasts
search_agent = Agent(
    name="MarketSearchAgent",
    model="gemini-2.0-flash",  # Required for google_search
    description="Searches the web for latest market news, analyst opinions, and stock forecasts",
    instruction="""You are a market research specialist. When asked about stocks or market trends:
1. Search for the latest news, analyst ratings, and market sentiment
2. Look for recent earnings reports, price targets, and institutional activity
3. Find any relevant macroeconomic factors affecting the stock/market
4. Always cite your sources with URLs when possible
5. Focus on recent information (last few days/weeks)

Provide a comprehensive summary of what you find.""",
    tools=[google_search]  # ONLY google_search - no other tools allowed
)

# Agent 2: Stock Data Agent - Has custom tools for price data
stock_data_agent = Agent(
    name="StockDataAgent", 
    model="gemini-2.5-flash",
    description="Gets live stock prices and analyzes technical trends",
    instruction="""You are a stock data analyst. When asked about a stock:
1. Get the current live price using get_live_stock_price
2. Analyze the trend using analyze_stock_trend
3. Report whether data is LIVE or DEMO/fallback
4. Provide clear price information and momentum analysis""",
    tools=[get_live_stock_price, analyze_stock_trend]
)

# Root Agent: Orchestrates the sub-agents using AgentTool
market_analyzer_agent = Agent(
    name="MarketAnalyzer",
    model="gemini-2.5-flash",
    description="Expert market analyst that combines web search with live stock data for predictions",
    instruction="""You are a friendly market analyst who explains things simply for beginner investors.

YOU HAVE ACCESS TO TWO SPECIALIST AGENTS:
1. MarketSearchAgent - Searches the web for latest news and analyst opinions  
2. StockDataAgent - Gets live stock prices and trends

WHEN USER ASKS ABOUT STOCK PREDICTIONS:
1. FIRST: Ask MarketSearchAgent for latest news
2. THEN: Ask StockDataAgent for current price data
3. FINALLY: Give a SIMPLE, CLEAR prediction WITH action recommendation

RESPONSE FORMAT (keep it simple and short):

📊 **[SYMBOL] Analysis**

**Price Right Now:** $X.XX (up/down X% today)

**What's Happening:**
• [One sentence summary of market sentiment]
• [One sentence about analyst opinion if available]

**📰 Recent News:**
• [1-2 lines of SPECIFIC current news about the company - product launches, earnings, partnerships, lawsuits, CEO statements, etc.]

**My Take:** 
[Use ONE of these simple verdicts with emoji]
- 🟢 **Likely to GO UP** - [one simple reason]
- 🔴 **Likely to GO DOWN** - [one simple reason]  
- 🟡 **UNCERTAIN/SIDEWAYS** - [one simple reason]

**💡 What I'd Suggest:**
[Give ONE of these clear action recommendations]
- ✅ **BUY NOW** - Good time to buy because [reason]
- ⏳ **WAIT** - Better to wait because [reason], consider buying if [condition]
- 🚫 **AVOID/SELL** - Not a good time because [reason]

**What to Watch:** [1-2 key things in simple words]

⚠️ *This is my opinion based on data - always verify and decide based on your own research!*

CRITICAL RULES:
- ALWAYS include Recent News with SPECIFIC headlines/events from your web search
- ALWAYS give a clear action recommendation (BUY/WAIT/AVOID) - never say "I cannot give advice"
- Use SIMPLE language a beginner can understand
- Keep it SHORT - max 15 lines
- Use emojis to make it scannable
- Be confident in your opinion but remind them to verify
- If uncertain, recommend WAIT with conditions for when to buy""",
    tools=[AgentTool(agent=search_agent), AgentTool(agent=stock_data_agent)]
)
