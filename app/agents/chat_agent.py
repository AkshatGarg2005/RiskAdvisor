"""
Portfolio Chat Agent using Google ADK.
Provides conversational answers about portfolio analysis WITH tool calling for calculations.
"""
import os
import json
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Tool function: Get portfolio summary
def get_portfolio_info(
    portfolio_value: float,
    risk_score: float,
    risk_level: str,
    holdings_count: int
) -> dict:
    """
    Get summarized information about the current portfolio.
    
    Args:
        portfolio_value: Total portfolio value in dollars
        risk_score: Current risk score (1-10)
        risk_level: Risk level (LOW, MODERATE, ELEVATED, HIGH)
        holdings_count: Number of holdings in portfolio
        
    Returns:
        Dictionary with portfolio summary
    """
    return {
        "portfolio_value": portfolio_value,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "holdings_count": holdings_count,
        "summary": f"Portfolio worth ${portfolio_value:,.2f} with {holdings_count} holdings. Risk score: {risk_score}/10 ({risk_level})"
    }


# Tool function: Simulate adding a stock
def simulate_add_stock(
    stock_symbol: str,
    amount: float,
    current_portfolio_value: float,
    current_risk_score: float
) -> dict:
    """
    Simulate what happens if user adds a stock to their portfolio.
    Calculates new portfolio value and estimated risk change.
    
    Args:
        stock_symbol: Stock ticker symbol to add (e.g., NVDA, AAPL, SPY)
        amount: Dollar amount to invest in the stock
        current_portfolio_value: Current total portfolio value
        current_risk_score: Current risk score (1-10)
        
    Returns:
        Dictionary with simulation results including new value and risk
    """
    # Calculate new portfolio value
    new_value = current_portfolio_value + amount
    
    # Estimate risk change based on stock type
    symbol_upper = stock_symbol.upper()
    
    # Index funds/ETFs typically reduce risk
    if symbol_upper in ["SPY", "VTI", "QQQ", "VOO", "IVV", "VT", "VEA", "BND", "AGG"]:
        risk_change = -0.5
        stock_type = "Index Fund/ETF"
        impact = "POSITIVE"
    # High-volatility stocks increase risk
    elif symbol_upper in ["TSLA", "NVDA", "AMD", "COIN", "GME", "AMC", "MARA", "RIOT"]:
        risk_change = 0.6
        stock_type = "High-Volatility Stock"
        impact = "CAUTIONARY"
    # Large-cap stable stocks - neutral/slight increase
    elif symbol_upper in ["AAPL", "MSFT", "GOOGL", "GOOG", "META", "AMZN", "JNJ", "PG", "KO", "WMT"]:
        risk_change = 0.2
        stock_type = "Large-Cap Stock"
        impact = "NEUTRAL"
    else:
        risk_change = 0.3
        stock_type = "Stock"
        impact = "NEUTRAL"
    
    new_risk_score = round(min(10, max(1, current_risk_score + risk_change)), 2)
    weight_in_new_portfolio = (amount / new_value) * 100
    
    return {
        "scenario": f"Add ${amount:,.0f} of {symbol_upper}",
        "stock_symbol": symbol_upper,
        "stock_type": stock_type,
        "amount_invested": amount,
        "current_portfolio_value": current_portfolio_value,
        "new_portfolio_value": new_value,
        "new_position_weight": round(weight_in_new_portfolio, 2),
        "current_risk_score": current_risk_score,
        "new_risk_score": new_risk_score,
        "risk_change": risk_change,
        "impact": impact,
        "analysis": f"Adding ${amount:,.0f} of {symbol_upper} ({stock_type}) would increase your portfolio to ${new_value:,.2f}. "
                   f"This would make {symbol_upper} {weight_in_new_portfolio:.1f}% of your portfolio. "
                   f"Risk score would change from {current_risk_score} to {new_risk_score} ({'+' if risk_change > 0 else ''}{risk_change:.1f} points)."
    }


# Tool function: Simulate selling a stock
def simulate_sell_stock(
    stock_symbol: str,
    amount: float,
    current_portfolio_value: float,
    current_risk_score: float
) -> dict:
    """
    Simulate what happens if user sells a stock from their portfolio.
    
    Args:
        stock_symbol: Stock ticker symbol to sell
        amount: Dollar amount to sell
        current_portfolio_value: Current total portfolio value
        current_risk_score: Current risk score (1-10)
        
    Returns:
        Dictionary with simulation results
    """
    new_value = max(0, current_portfolio_value - amount)
    
    # Selling typically reduces concentration (slight risk reduction) 
    # unless it reduces diversification
    risk_change = 0.3 if current_portfolio_value > 0 else 0
    new_risk_score = round(min(10, max(1, current_risk_score + risk_change)), 2)
    
    return {
        "scenario": f"Sell ${amount:,.0f} of {stock_symbol.upper()}",
        "stock_symbol": stock_symbol.upper(),
        "amount_sold": amount,
        "current_portfolio_value": current_portfolio_value,
        "new_portfolio_value": new_value,
        "current_risk_score": current_risk_score,
        "new_risk_score": new_risk_score,
        "risk_change": risk_change,
        "impact": "CAUTIONARY",
        "analysis": f"Selling ${amount:,.0f} of {stock_symbol.upper()} would reduce your portfolio to ${new_value:,.2f}. "
                   f"Consider the impact on diversification. Risk score would change to {new_risk_score}."
    }


# Tool function: Compare scenarios
def compare_investment_options(
    option1_symbol: str,
    option2_symbol: str,
    amount: float,
    current_portfolio_value: float,
    current_risk_score: float
) -> dict:
    """
    Compare two investment options side by side.
    
    Args:
        option1_symbol: First stock symbol to compare
        option2_symbol: Second stock symbol to compare
        amount: Dollar amount to invest
        current_portfolio_value: Current portfolio value
        current_risk_score: Current risk score
        
    Returns:
        Dictionary comparing both options
    """
    result1 = simulate_add_stock(option1_symbol, amount, current_portfolio_value, current_risk_score)
    result2 = simulate_add_stock(option2_symbol, amount, current_portfolio_value, current_risk_score)
    
    # Determine which is better for risk
    better_for_risk = option1_symbol if result1["new_risk_score"] < result2["new_risk_score"] else option2_symbol
    
    return {
        "comparison": f"{option1_symbol.upper()} vs {option2_symbol.upper()} - ${amount:,.0f} investment",
        "option1": result1,
        "option2": result2,
        "recommendation": f"{better_for_risk.upper()} would result in a lower risk score ({min(result1['new_risk_score'], result2['new_risk_score'])})",
        "risk_difference": abs(result1["new_risk_score"] - result2["new_risk_score"])
    }


def get_portfolio_summary(portfolio_data: dict) -> str:
    """
    Convert portfolio analysis data into a detailed text summary for the agent.
    """
    if not portfolio_data:
        return "No portfolio data available."
    
    summary_parts = []
    summary_parts.append("PORTFOLIO DATA:")
    summary_parts.append(f"  Total Value: ${portfolio_data.get('total_value', 0):,.2f}")
    summary_parts.append(f"  Risk Score: {portfolio_data.get('risk_score', 'N/A')}/10")
    summary_parts.append(f"  Risk Level: {portfolio_data.get('risk_level', 'N/A')}")
    
    holdings = portfolio_data.get('holdings', [])
    if holdings:
        summary_parts.append(f"\nHOLDINGS ({len(holdings)} positions):")
        for h in holdings:
            symbol = h.get('symbol', 'Unknown')
            value = h.get('value', 0)
            summary_parts.append(f"  - {symbol}: ${value:,.2f}" if isinstance(value, (int, float)) else f"  - {symbol}")
    
    return "\n".join(summary_parts)


# Define the Portfolio Chat Agent with tools
portfolio_chat_agent = LlmAgent(
    name="PortfolioChatAgent",
    model="gemini-2.5-flash",
    description="Conversational investment advisor that answers questions about portfolios and can run calculations",
    instruction="""You are an expert investment advisor assistant. You can help users understand their portfolio and run calculations using your tools.

AVAILABLE TOOLS:
- simulate_add_stock: Calculate what happens if user buys a stock
- simulate_sell_stock: Calculate what happens if user sells a stock  
- compare_investment_options: Compare two investment choices
- get_portfolio_info: Get portfolio summary

WHEN TO USE TOOLS:
- User asks "what if I buy/add X of Y" -> Use simulate_add_stock
- User asks about selling -> Use simulate_sell_stock
- User asks to compare options -> Use compare_investment_options
- User asks about their portfolio -> Use get_portfolio_info

ALWAYS use the tools when the user asks about scenarios. The tools do REAL calculations.
After getting tool results, explain them conversationally to the user.
Reference specific numbers from the tool results in your response.
""",
    tools=[simulate_add_stock, simulate_sell_stock, compare_investment_options, get_portfolio_info],
    output_key="chat_response"
)
