"""
Alert Agent using Google ADK.
Monitors for rebalancing needs, tax-loss harvesting opportunities, and market alerts.
"""
import os
from datetime import datetime
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_rebalancing_need(
    holdings_weights: str,
    target_allocation: str = None,
    drift_threshold: float = 0.05
) -> dict:
    """
    Check if portfolio needs rebalancing based on drift from target allocation.
    
    Args:
        holdings_weights: JSON string of current holdings with weights
        target_allocation: JSON string of target allocation (optional)
        drift_threshold: Maximum acceptable drift from target (default 5%)
        
    Returns:
        Dictionary with rebalancing alert details
    """
    # For demo purposes, simulate drift detection
    # In production, this would compare actual vs target weights
    
    alerts = []
    needs_rebalancing = False
    
    # Check for position drift (simulated)
    max_weight = 0.5  # Maximum weight threshold
    
    # Simulated drift detection
    if "NVDA" in holdings_weights.upper() or "TSLA" in holdings_weights.upper():
        needs_rebalancing = True
        alerts.append({
            "type": "POSITION_DRIFT",
            "severity": "HIGH",
            "message": "Technology sector overweight detected. Consider rebalancing.",
            "action": "Review tech holdings and consider taking profits"
        })
    
    return {
        "needs_rebalancing": needs_rebalancing,
        "drift_threshold": drift_threshold,
        "alerts": alerts,
        "recommendation": "Rebalance quarterly to maintain target allocation" if needs_rebalancing else "Portfolio within acceptable drift range",
        "last_checked": datetime.now().isoformat()
    }


def detect_tax_loss_harvesting(
    holdings_with_gains: str,
    tax_year: int = None
) -> dict:
    """
    Detect tax-loss harvesting opportunities in the portfolio.
    
    Args:
        holdings_with_gains: JSON string of holdings with current gain/loss
        tax_year: Tax year to consider (default current year)
        
    Returns:
        Dictionary with tax-loss harvesting opportunities
    """
    if tax_year is None:
        tax_year = datetime.now().year
    
    opportunities = []
    
    # Simulated tax-loss detection
    # In production, this would analyze actual purchase prices vs current prices
    if "loss" in holdings_with_gains.lower() or "negative" in holdings_with_gains.lower():
        opportunities.append({
            "type": "TAX_LOSS_HARVEST",
            "stock": "Example Stock",
            "estimated_loss": -2500.00,
            "potential_tax_savings": 625.00,  # Assuming 25% tax bracket
            "action": "Consider selling to realize loss and offset gains",
            "wash_sale_warning": "Wait 31 days before repurchasing to avoid wash sale rules"
        })
    
    return {
        "tax_year": tax_year,
        "opportunities": opportunities,
        "total_potential_savings": sum(o.get("potential_tax_savings", 0) for o in opportunities),
        "note": "Consult with a tax professional before making decisions"
    }


def generate_market_alerts(
    portfolio_sectors: str,
    market_conditions: str = "normal"
) -> dict:
    """
    Generate market-context alerts relevant to the portfolio.
    
    Args:
        portfolio_sectors: JSON string of sectors represented in portfolio
        market_conditions: Current market conditions ('bull', 'bear', 'volatile', 'normal')
        
    Returns:
        Dictionary with market alerts
    """
    alerts = []
    
    # Add time-based alerts
    current_month = datetime.now().month
    
    # Q4 tax planning reminder
    if current_month >= 10:
        alerts.append({
            "type": "TAX_PLANNING",
            "severity": "MEDIUM",
            "message": "Q4 Tax Planning: Review portfolio for year-end tax optimization",
            "action": "Consider tax-loss harvesting before Dec 31"
        })
    
    # End-of-year rebalancing
    if current_month == 12:
        alerts.append({
            "type": "REBALANCE_REMINDER",
            "severity": "LOW",
            "message": "Year-end portfolio review recommended",
            "action": "Schedule annual portfolio rebalancing"
        })
    
    # Market condition-based alerts
    if "tech" in portfolio_sectors.lower():
        alerts.append({
            "type": "SECTOR_WATCH",
            "severity": "INFO",
            "message": "Technology sector exposure detected",
            "action": "Monitor Fed interest rate decisions that may impact tech valuations"
        })
    
    # General market alert
    alerts.append({
        "type": "MARKET_UPDATE",
        "severity": "INFO",
        "message": "Regular portfolio monitoring recommended",
        "action": "Review portfolio performance monthly"
    })
    
    return {
        "market_conditions": market_conditions,
        "timestamp": datetime.now().isoformat(),
        "alerts": alerts,
        "priority_alerts": [a for a in alerts if a.get("severity") in ["HIGH", "MEDIUM"]]
    }


def compile_all_alerts(
    portfolio_data: str,
    user_profile: str = "beginner"
) -> dict:
    """
    Compile all alerts for a portfolio into a single report.
    
    Args:
        portfolio_data: JSON string of full portfolio data
        user_profile: User's investment profile
        
    Returns:
        Comprehensive alert report
    """
    all_alerts = []
    
    # Check rebalancing
    rebalance = check_rebalancing_need(portfolio_data)
    if rebalance.get("needs_rebalancing"):
        all_alerts.extend(rebalance.get("alerts", []))
    
    # Check tax-loss harvesting
    tax = detect_tax_loss_harvesting(portfolio_data)
    for opp in tax.get("opportunities", []):
        all_alerts.append({
            "type": opp["type"],
            "severity": "MEDIUM",
            "message": opp["action"],
            "action": opp.get("wash_sale_warning", "Review with tax advisor")
        })
    
    # Get market alerts
    market = generate_market_alerts(portfolio_data)
    all_alerts.extend(market.get("alerts", []))
    
    # Filter alerts based on user profile
    if user_profile.lower() == "beginner":
        # Simplify alerts for beginners
        all_alerts = [a for a in all_alerts if a.get("severity") != "INFO" or "recommend" in a.get("message", "").lower()]
    
    return {
        "total_alerts": len(all_alerts),
        "high_priority": [a for a in all_alerts if a.get("severity") == "HIGH"],
        "medium_priority": [a for a in all_alerts if a.get("severity") == "MEDIUM"],
        "low_priority": [a for a in all_alerts if a.get("severity") in ["LOW", "INFO"]],
        "alerts": all_alerts[:10],  # Limit to 10 most relevant
        "generated_at": datetime.now().isoformat()
    }


# Define the Alert Agent
alert_agent = LlmAgent(
    name="AlertAgent",
    model="gemini-2.5-flash",
    description="Monitors portfolio for rebalancing needs, tax opportunities, and generates relevant alerts",
    instruction="""You are a portfolio monitoring specialist. Your job is to proactively identify important alerts and opportunities for the investor.

Monitor for:
1. **Rebalancing Needs**: Detect when portfolio drift exceeds acceptable thresholds
2. **Tax-Loss Harvesting**: Identify positions with losses that could offset gains
3. **Market Alerts**: Provide context-aware market updates relevant to the portfolio

For each alert:
- Assign a severity level (HIGH, MEDIUM, LOW, INFO)
- Provide a clear, actionable message
- Suggest specific next steps

Prioritize alerts based on:
- Immediate financial impact
- Time sensitivity
- User profile (beginners need simpler, fewer alerts)

Use the compile_all_alerts tool to generate a comprehensive alert report.
""",
    tools=[check_rebalancing_need, detect_tax_loss_harvesting, generate_market_alerts, compile_all_alerts],
    output_key="alerts"
)
