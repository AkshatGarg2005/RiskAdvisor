"""
Scenario Agent using Google ADK.
Models "what-if" scenarios for portfolio changes.
"""
import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def simulate_scenario(
    scenario_type: str,
    current_portfolio_value: float,
    current_risk_score: float,
    stock_symbol: str,
    change_amount: float
) -> dict:
    """
    Simulate a what-if scenario for portfolio changes.
    
    Args:
        scenario_type: Type of scenario ('add_stock', 'remove_stock', 'increase_position', 'decrease_position')
        current_portfolio_value: Current total portfolio value
        current_risk_score: Current risk score (1-10)
        stock_symbol: Stock symbol involved in the scenario
        change_amount: Amount of change (in dollars or percentage)
        
    Returns:
        Dictionary with scenario simulation results
    """
    # Calculate simulated impacts
    if scenario_type == "add_stock":
        # Adding a new stock typically increases diversification
        new_value = current_portfolio_value + change_amount
        weight_change = change_amount / new_value
        
        # Estimate risk change based on typical stock volatility
        if stock_symbol.upper() in ["SPY", "VTI", "QQQ"]:
            # Index funds typically reduce risk
            risk_change = -0.8
        elif stock_symbol.upper() in ["TSLA", "NVDA", "COIN"]:
            # High-volatility stocks increase risk
            risk_change = 0.6
        else:
            risk_change = 0.2  # Neutral impact
        
        new_risk = round(min(10, max(1, current_risk_score + risk_change)), 2)
        
        return {
            "scenario": f"Add ${change_amount:,.0f} to {stock_symbol}",
            "scenario_type": scenario_type,
            "current_value": current_portfolio_value,
            "new_value": new_value,
            "current_risk_score": current_risk_score,
            "new_risk_score": new_risk,
            "risk_change": round(risk_change, 2),
            "impact": "POSITIVE" if risk_change < 0 else "NEGATIVE" if risk_change > 0.3 else "NEUTRAL",
            "analysis": f"Adding {stock_symbol} would change portfolio value to ${new_value:,.2f} and {'reduce' if risk_change < 0 else 'increase'} risk by {abs(risk_change):.1f} points."
        }
    
    elif scenario_type == "remove_stock":
        # Removing a stock reduces diversification
        new_value = current_portfolio_value - change_amount
        risk_change = 0.3 if current_portfolio_value > 0 else 0
        new_risk = round(min(10, max(1, current_risk_score + risk_change)), 2)
        
        return {
            "scenario": f"Sell {stock_symbol} (${change_amount:,.0f})",
            "scenario_type": scenario_type,
            "current_value": current_portfolio_value,
            "new_value": max(0, new_value),
            "current_risk_score": current_risk_score,
            "new_risk_score": new_risk,
            "risk_change": round(risk_change, 2),
            "impact": "CAUTIONARY",
            "analysis": f"Selling {stock_symbol} would reduce portfolio to ${new_value:,.2f}. Consider the concentration impact on remaining positions."
        }
    
    elif scenario_type == "increase_position":
        # Increasing position in existing stock
        new_value = current_portfolio_value + change_amount
        risk_change = 0.4  # Generally increases concentration risk
        new_risk = round(min(10, max(1, current_risk_score + risk_change)), 2)
        
        return {
            "scenario": f"Increase {stock_symbol} by ${change_amount:,.0f}",
            "scenario_type": scenario_type,
            "current_value": current_portfolio_value,
            "new_value": new_value,
            "current_risk_score": current_risk_score,
            "new_risk_score": new_risk,
            "risk_change": round(risk_change, 2),
            "impact": "CAUTIONARY",
            "analysis": f"Increasing position in {stock_symbol} would add ${change_amount:,.0f} but also increase concentration risk."
        }
    
    else:  # decrease_position
        new_value = current_portfolio_value - change_amount
        risk_change = -0.2  # May reduce concentration
        new_risk = round(min(10, max(1, current_risk_score + risk_change)), 2)
        
        return {
            "scenario": f"Decrease {stock_symbol} by ${change_amount:,.0f}",
            "scenario_type": scenario_type,
            "current_value": current_portfolio_value,
            "new_value": max(0, new_value),
            "current_risk_score": current_risk_score,
            "new_risk_score": new_risk,
            "risk_change": round(risk_change, 2),
            "impact": "POSITIVE",
            "analysis": f"Reducing {stock_symbol} position could improve diversification and lower concentration risk."
        }


def run_multiple_scenarios(
    portfolio_value: float,
    risk_score: float,
    largest_holding: str,
    largest_holding_value: float
) -> dict:
    """
    Run multiple common scenarios for comparison.
    
    Args:
        portfolio_value: Current portfolio value
        risk_score: Current risk score
        largest_holding: Symbol of largest holding
        largest_holding_value: Value of largest holding
        
    Returns:
        Dictionary with multiple scenario comparisons
    """
    scenarios = []
    
    # Scenario 1: Add index fund
    scenarios.append(simulate_scenario(
        "add_stock",
        portfolio_value,
        risk_score,
        "SPY",
        10000
    ))
    
    # Scenario 2: Increase largest position
    scenarios.append(simulate_scenario(
        "increase_position",
        portfolio_value,
        risk_score,
        largest_holding,
        5000
    ))
    
    # Scenario 3: Decrease largest position
    scenarios.append(simulate_scenario(
        "decrease_position",
        portfolio_value,
        risk_score,
        largest_holding,
        largest_holding_value * 0.3  # Reduce by 30%
    ))
    
    return {
        "scenarios": scenarios,
        "recommendation": get_scenario_recommendation(scenarios)
    }


def get_scenario_recommendation(scenarios: list) -> str:
    """Get recommendation based on scenario analysis."""
    best_scenario = min(scenarios, key=lambda x: x.get("new_risk_score", 10))
    return f"Based on analysis, '{best_scenario['scenario']}' would result in the most favorable risk profile (Risk Score: {best_scenario['new_risk_score']})."


# Define the Scenario Agent
scenario_agent = LlmAgent(
    name="ScenarioAgent",
    model="gemini-2.5-flash",
    description="Models what-if scenarios to help investors understand the impact of portfolio changes",
    instruction="""You are a portfolio scenario analyst. Your job is to help investors understand how different actions would affect their portfolio risk and returns.

For each portfolio:
1. Identify potential scenarios to model (add stocks, remove stocks, rebalance)
2. Calculate the impact of each scenario on risk score and portfolio value
3. Compare scenarios and highlight the best options
4. Present results in a clear, comparative format

Common scenarios to model:
- Adding $10,000 to an index fund (SPY/VTI)
- Increasing position in largest holding
- Reducing concentrated positions
- Adding diversification through new sectors

Use the simulate_scenario and run_multiple_scenarios tools to generate analysis.

Format output to show:
- Current state
- Each scenario with projected changes
- Recommendation based on risk improvement
""",
    tools=[simulate_scenario, run_multiple_scenarios],
    output_key="scenarios"
)
