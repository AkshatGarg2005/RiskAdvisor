"""
Stock Analyzer Agent using Google ADK.
Analyzes individual stocks with risk assessment and Hold/Sell recommendations.
Uses Alpha Vantage for real data with fallback to mock data.
"""
import os
import requests
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpha Vantage API
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Mock volatility data for fallback
MOCK_VOLATILITY = {
    "AAPL": 0.28, "GOOGL": 0.32, "MSFT": 0.25, "AMZN": 0.35, 
    "TSLA": 0.55, "NVDA": 0.52, "META": 0.40, "SPY": 0.15,
    "QQQ": 0.22, "VTI": 0.14, "INFY": 0.30, "TCS": 0.28
}


def get_stock_data(symbol: str) -> dict:
    """
    Fetch stock data from Alpha Vantage API.
    Falls back to mock data if API fails.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with stock data including price, change, volume
    """
    symbol = symbol.upper().strip()
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    if api_key:
        try:
            # Fetch current quote
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": api_key
            }
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                return {
                    "symbol": symbol,
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": quote.get("10. change percent", "0%"),
                    "volume": int(quote.get("06. volume", 0)),
                    "previous_close": float(quote.get("08. previous close", 0)),
                    "source": "alpha_vantage"
                }
        except Exception as e:
            print(f"⚠️ Alpha Vantage API error for {symbol}: {e}")
    
    # Fallback to mock data
    mock_prices = {
        "AAPL": 195.50, "GOOGL": 142.80, "MSFT": 378.90, "AMZN": 178.25,
        "TSLA": 248.50, "NVDA": 495.80, "META": 325.40, "SPY": 458.25,
        "QQQ": 392.80, "VTI": 238.50, "INFY": 18.25, "TCS": 3850.00
    }
    
    return {
        "symbol": symbol,
        "price": mock_prices.get(symbol, 100.0),
        "change": 0.0,
        "change_percent": "0%",
        "volume": 0,
        "previous_close": mock_prices.get(symbol, 100.0),
        "source": "mock_fallback"
    }


def analyze_stock_risk(
    symbol: str,
    quantity: float,
    purchase_price: float,
    current_price: float,
    portfolio_weight: float
) -> dict:
    """
    Analyze individual stock risk level.
    
    Args:
        symbol: Stock ticker symbol
        quantity: Number of shares held
        purchase_price: Original purchase price per share
        current_price: Current market price
        portfolio_weight: Percentage of portfolio this stock represents
        
    Returns:
        Dictionary with risk analysis for this stock
    """
    symbol = symbol.upper()
    
    # Calculate gain/loss
    gain_loss = (current_price - purchase_price) * quantity
    gain_loss_percent = ((current_price - purchase_price) / purchase_price) * 100 if purchase_price > 0 else 0
    
    # Get volatility (use mock if not available)
    volatility = MOCK_VOLATILITY.get(symbol, 0.35)
    
    # Calculate risk score for this stock (1-10)
    # Factors: volatility, concentration (portfolio weight), loss position
    volatility_risk = min(volatility * 10, 5)  # 0-5 points
    concentration_risk = min(portfolio_weight / 10, 3)  # 0-3 points if > 30%
    loss_risk = 2 if gain_loss_percent < -10 else (1 if gain_loss_percent < 0 else 0)
    
    stock_risk_score = round(volatility_risk + concentration_risk + loss_risk, 1)
    stock_risk_score = min(10, max(1, stock_risk_score))
    
    # Determine risk level
    if stock_risk_score <= 3:
        risk_level = "LOW"
    elif stock_risk_score <= 5:
        risk_level = "MODERATE"
    elif stock_risk_score <= 7:
        risk_level = "ELEVATED"
    else:
        risk_level = "HIGH"
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "purchase_price": purchase_price,
        "quantity": quantity,
        "current_value": round(current_price * quantity, 2),
        "gain_loss": round(gain_loss, 2),
        "gain_loss_percent": round(gain_loss_percent, 2),
        "volatility": round(volatility * 100, 1),
        "portfolio_weight": round(portfolio_weight, 1),
        "risk_score": stock_risk_score,
        "risk_level": risk_level
    }


def generate_stock_recommendation(
    symbol: str,
    risk_score: float,
    gain_loss_percent: float,
    portfolio_weight: float,
    volatility: float
) -> dict:
    """
    Generate Hold/Sell recommendation for a stock.
    
    Args:
        symbol: Stock ticker symbol
        risk_score: Individual stock risk score (1-10)
        gain_loss_percent: Current gain or loss percentage
        portfolio_weight: Percentage of portfolio
        volatility: Stock volatility percentage
        
    Returns:
        Dictionary with recommendation and reasoning
    """
    symbol = symbol.upper()
    
    # Decision logic
    reasons = []
    recommendation = "HOLD"
    confidence = "MEDIUM"
    
    # Check for SELL signals
    sell_signals = 0
    
    if risk_score >= 7:
        sell_signals += 1
        reasons.append(f"High risk score ({risk_score}/10)")
    
    if gain_loss_percent < -15:
        sell_signals += 1
        reasons.append(f"Significant loss ({gain_loss_percent:.1f}%)")
    
    if portfolio_weight > 35:
        sell_signals += 1
        reasons.append(f"Over-concentrated ({portfolio_weight:.1f}% of portfolio)")
    
    if volatility > 45:
        sell_signals += 1
        reasons.append(f"High volatility ({volatility:.1f}%)")
    
    # Check for strong HOLD/BUY signals
    hold_signals = 0
    
    if gain_loss_percent > 20:
        hold_signals += 1
        reasons.append(f"Strong gains ({gain_loss_percent:.1f}%)")
    
    if risk_score <= 3:
        hold_signals += 1
        reasons.append(f"Low risk profile")
    
    if volatility < 20 and portfolio_weight < 25:
        hold_signals += 1
        reasons.append("Well-balanced stable position")
    
    # Determine recommendation
    if sell_signals >= 2:
        recommendation = "SELL"
        confidence = "HIGH" if sell_signals >= 3 else "MEDIUM"
    elif sell_signals == 1 and hold_signals == 0:
        recommendation = "REDUCE"
        confidence = "MEDIUM"
    elif hold_signals >= 2:
        recommendation = "HOLD"
        confidence = "HIGH"
    else:
        recommendation = "HOLD"
        confidence = "LOW"
    
    # Build action text
    if recommendation == "SELL":
        action = f"Consider selling {symbol} to reduce portfolio risk"
    elif recommendation == "REDUCE":
        action = f"Consider reducing your {symbol} position by 25-50%"
    else:
        action = f"Keep holding {symbol} - no immediate action needed"
    
    return {
        "symbol": symbol,
        "recommendation": recommendation,
        "confidence": confidence,
        "action": action,
        "reasons": reasons if reasons else ["Position is balanced and within normal parameters"]
    }


def analyze_all_stocks(holdings_json: str) -> dict:
    """
    Analyze all stocks in a portfolio and generate recommendations.
    
    Args:
        holdings_json: JSON string or list of holdings with symbol, value, weight, individual_volatility
        
    Returns:
        Dictionary with analysis for each stock
    """
    import json
    
    try:
        holdings = json.loads(holdings_json) if isinstance(holdings_json, str) else holdings_json
    except:
        return {"error": "Invalid holdings data", "stock_analyses": []}
    
    if not holdings:
        return {"stock_count": 0, "high_risk_count": 0, "sell_recommendations": 0, "stock_analyses": []}
    
    stock_analyses = []
    total_value = sum(h.get("value", 0) for h in holdings)
    
    for holding in holdings:
        symbol = holding.get("symbol", "UNKNOWN")
        # Get value directly from holdings_analysis (already calculated)
        value = holding.get("value", 0)
        # Use weight from data, or calculate it
        weight = holding.get("weight", (value / total_value * 100) if total_value > 0 else 0)
        # Use individual_volatility if provided, else use mock
        volatility = holding.get("individual_volatility", MOCK_VOLATILITY.get(symbol.upper(), 0.35))
        
        # For gain/loss, we'd need purchase data - use 0% if not available
        # In production, this would come from the original holdings
        purchase_price = holding.get("purchase_price", 0)
        current_price = holding.get("current_price", 0)
        quantity = holding.get("quantity", 0)
        
        # If we have price data, calculate gain/loss
        if purchase_price > 0 and current_price > 0:
            gain_loss_percent = ((current_price - purchase_price) / purchase_price) * 100
            gain_loss = (current_price - purchase_price) * quantity
        else:
            gain_loss_percent = 0
            gain_loss = 0
        
        # Calculate risk score based on available data
        # Factors: volatility, concentration (portfolio weight)
        volatility_risk = min(volatility * 10, 5)  # 0-5 points (volatility is 0-1 scale)
        concentration_risk = min(weight / 10, 3)  # 0-3 points
        loss_risk = 2 if gain_loss_percent < -10 else (1 if gain_loss_percent < 0 else 0)
        
        stock_risk_score = round(volatility_risk + concentration_risk + loss_risk, 1)
        stock_risk_score = min(10, max(1, stock_risk_score))
        
        # Determine risk level
        if stock_risk_score <= 3:
            risk_level = "LOW"
        elif stock_risk_score <= 5:
            risk_level = "MODERATE"
        elif stock_risk_score <= 7:
            risk_level = "ELEVATED"
        else:
            risk_level = "HIGH"
        
        # Generate recommendation
        recommendation = generate_stock_recommendation(
            symbol=symbol,
            risk_score=stock_risk_score,
            gain_loss_percent=gain_loss_percent,
            portfolio_weight=weight,
            volatility=volatility * 100  # Convert to percentage
        )
        
        stock_analyses.append({
            "symbol": symbol,
            "current_value": round(value, 2),
            "portfolio_weight": round(weight, 1),
            "volatility": round(volatility * 100, 1),
            "gain_loss_percent": round(gain_loss_percent, 1),
            "risk_score": stock_risk_score,
            "risk_level": risk_level,
            **recommendation
        })
    
    # Sort by risk score (highest first)
    stock_analyses.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "stock_count": len(stock_analyses),
        "high_risk_count": sum(1 for s in stock_analyses if s["risk_level"] in ["HIGH", "ELEVATED"]),
        "sell_recommendations": sum(1 for s in stock_analyses if s["recommendation"] in ["SELL", "REDUCE"]),
        "stock_analyses": stock_analyses
    }


# Define the Stock Analyzer Agent with tools
stock_analyzer_agent = LlmAgent(
    name="StockAnalyzer",
    model="gemini-2.5-flash",
    description="Analyzes individual stocks in a portfolio with risk levels and Hold/Sell recommendations",
    instruction="""You are an expert stock analyst. For each stock in a portfolio, you analyze:
1. Individual risk level based on volatility, concentration, and performance
2. Whether to HOLD, REDUCE, or SELL the position
3. Clear reasoning for your recommendation

Use the analyze_all_stocks tool to get detailed analysis for all holdings.
After receiving the results, summarize the key findings and highlight any stocks that need attention.

Always be clear about which stocks are high-risk and explain why.
Provide actionable advice for each stock position.
""",
    tools=[get_stock_data, analyze_stock_risk, generate_stock_recommendation, analyze_all_stocks],
    output_key="stock_analysis"
)
