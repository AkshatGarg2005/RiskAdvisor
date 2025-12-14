"""
Price fetching utilities using Alpha Vantage API.
Includes caching to avoid rate limits on free tier.
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache

# Alpha Vantage API endpoint
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Cache for storing price data (simulates API calls for demo)
_price_cache: dict = {}

# Mock data for testing (to avoid API rate limits)
MOCK_PRICES = {
    "AAPL": {"current": 195.50, "history": [190.0, 192.5, 188.0, 195.0, 193.5, 196.0, 194.0, 195.5]},
    "GOOGL": {"current": 142.80, "history": [138.0, 140.5, 139.0, 141.5, 143.0, 144.0, 142.5, 142.8]},
    "MSFT": {"current": 378.90, "history": [370.0, 372.5, 375.0, 374.0, 376.5, 378.0, 377.5, 378.9]},
    "AMZN": {"current": 178.25, "history": [172.0, 174.5, 173.0, 175.5, 176.0, 177.5, 178.0, 178.25]},
    "TSLA": {"current": 248.50, "history": [240.0, 245.5, 242.0, 250.0, 255.0, 248.0, 246.5, 248.5]},
    "NVDA": {"current": 495.80, "history": [480.0, 485.5, 490.0, 492.0, 498.0, 500.5, 495.0, 495.8]},
    "META": {"current": 325.40, "history": [318.0, 320.5, 322.0, 324.0, 326.5, 328.0, 325.0, 325.4]},
    "SPY": {"current": 458.25, "history": [450.0, 452.5, 454.0, 455.5, 456.0, 457.5, 458.0, 458.25]},
    "QQQ": {"current": 392.80, "history": [385.0, 387.5, 389.0, 390.5, 391.0, 392.5, 392.0, 392.8]},
    "VTI": {"current": 238.50, "history": [232.0, 234.5, 235.0, 236.5, 237.0, 238.0, 238.5, 238.5]},
    "RELIANCE.BSE": {"current": 2520.50, "history": [2450.0, 2480.5, 2490.0, 2500.5, 2510.0, 2515.5, 2520.0, 2520.5]},
    "INFY": {"current": 18.25, "history": [17.5, 17.8, 18.0, 18.2, 18.1, 18.3, 18.2, 18.25]},
    "TCS": {"current": 3850.00, "history": [3780.0, 3800.5, 3820.0, 3835.5, 3840.0, 3845.5, 3848.0, 3850.0]},
}


def get_api_key() -> str:
    """Get Alpha Vantage API key from environment."""
    return os.getenv("ALPHA_VANTAGE_API_KEY", "")


def fetch_current_price(symbol: str, use_mock: bool = True) -> dict:
    """
    Fetch current stock price for a symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        use_mock: If True, use mock data to avoid API rate limits
        
    Returns:
        dict with 'status', 'price', and optionally 'error'
    """
    symbol = symbol.upper().strip()
    
    # Use mock data for demo/testing
    if use_mock and symbol in MOCK_PRICES:
        return {
            "status": "success",
            "symbol": symbol,
            "price": MOCK_PRICES[symbol]["current"],
            "source": "mock"
        }
    
    # Check cache first
    cache_key = f"{symbol}_current"
    if cache_key in _price_cache:
        cache_entry = _price_cache[cache_key]
        if datetime.now() - cache_entry["timestamp"] < timedelta(minutes=5):
            return cache_entry["data"]
    
    # Call Alpha Vantage API
    api_key = get_api_key()
    if not api_key:
        return {
            "status": "error",
            "symbol": symbol,
            "error": "Alpha Vantage API key not configured"
        }
    
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            result = {
                "status": "success",
                "symbol": symbol,
                "price": price,
                "source": "alpha_vantage"
            }
            # Cache the result
            _price_cache[cache_key] = {
                "timestamp": datetime.now(),
                "data": result
            }
            return result
        else:
            # Check if rate limited
            if "Note" in data or "Information" in data:
                # Fall back to mock if available
                if symbol in MOCK_PRICES:
                    return {
                        "status": "success",
                        "symbol": symbol,
                        "price": MOCK_PRICES[symbol]["current"],
                        "source": "mock_fallback"
                    }
                return {
                    "status": "error",
                    "symbol": symbol,
                    "error": "API rate limit exceeded"
                }
            return {
                "status": "error",
                "symbol": symbol,
                "error": f"No price data available for {symbol}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "symbol": symbol,
            "error": f"API request failed: {str(e)}"
        }


def fetch_historical_prices(symbol: str, days: int = 30, use_mock: bool = True) -> dict:
    """
    Fetch historical stock prices for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days of history to fetch
        use_mock: If True, use mock data to avoid API rate limits
        
    Returns:
        dict with 'status', 'prices' (list of floats), and optionally 'error'
    """
    symbol = symbol.upper().strip()
    
    # Use mock data for demo/testing
    if use_mock and symbol in MOCK_PRICES:
        # Extend mock data with some variance
        base_prices = MOCK_PRICES[symbol]["history"]
        extended_prices = []
        for i in range(days):
            idx = i % len(base_prices)
            variance = (i % 5 - 2) * 0.5  # Small variance
            extended_prices.append(base_prices[idx] + variance)
        return {
            "status": "success",
            "symbol": symbol,
            "prices": extended_prices[-days:],
            "source": "mock"
        }
    
    # Call Alpha Vantage API for historical data
    api_key = get_api_key()
    if not api_key:
        return {
            "status": "error",
            "symbol": symbol,
            "error": "Alpha Vantage API key not configured"
        }
    
    try:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",  # Last 100 data points
            "apikey": api_key
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            prices = []
            for date in sorted(time_series.keys())[-days:]:
                close_price = float(time_series[date]["4. close"])
                prices.append(close_price)
            return {
                "status": "success",
                "symbol": symbol,
                "prices": prices,
                "source": "alpha_vantage"
            }
        else:
            # Fall back to mock if available
            if symbol in MOCK_PRICES:
                base_prices = MOCK_PRICES[symbol]["history"]
                return {
                    "status": "success",
                    "symbol": symbol,
                    "prices": base_prices,
                    "source": "mock_fallback"
                }
            return {
                "status": "error",
                "symbol": symbol,
                "error": f"No historical data available for {symbol}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "symbol": symbol,
            "error": f"API request failed: {str(e)}"
        }


def enrich_portfolio_with_prices(holdings: list[dict], use_mock: bool = True) -> list[dict]:
    """
    Enrich portfolio holdings with current prices and historical data.
    
    Args:
        holdings: List of holding dicts with 'symbol', 'quantity', 'purchase_price'
        use_mock: If True, use mock data
        
    Returns:
        List of enriched holdings with current_price and historical_prices
    """
    enriched = []
    for holding in holdings:
        symbol = holding.get("symbol", "").upper()
        enriched_holding = dict(holding)
        
        # Fetch current price
        current_result = fetch_current_price(symbol, use_mock)
        if current_result["status"] == "success":
            enriched_holding["current_price"] = current_result["price"]
        else:
            enriched_holding["current_price"] = holding.get("purchase_price", 0)
            enriched_holding["price_error"] = current_result.get("error")
        
        # Fetch historical prices
        historical_result = fetch_historical_prices(symbol, days=30, use_mock=use_mock)
        if historical_result["status"] == "success":
            enriched_holding["historical_prices"] = historical_result["prices"]
        else:
            enriched_holding["historical_prices"] = []
        
        enriched.append(enriched_holding)
    
    return enriched
