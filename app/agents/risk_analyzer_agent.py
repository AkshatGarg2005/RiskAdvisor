"""
Risk Analyzer Agent using Google ADK.
Calculates portfolio volatility, concentration risk, and correlation.
"""
import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Tool function for risk analysis
def analyze_risk(
    portfolio_data: str,
    volatility: float,
    concentration: float,
    correlation: float,
    risk_score: float
) -> dict:
    """
    Analyze portfolio risk and provide detailed breakdown.
    
    Args:
        portfolio_data: JSON string of portfolio holdings with values and weights
        volatility: Calculated portfolio volatility (0-1 scale)
        concentration: HHI concentration index (0-1 scale)
        correlation: Average correlation between holdings (0-1 scale)
        risk_score: Overall risk score (1-10 scale)
        
    Returns:
        Dictionary with risk analysis results and interpretation
    """
    # Interpret risk level
    if risk_score <= 3:
        risk_level = "LOW"
        interpretation = "Your portfolio has low risk. It is well-diversified with stable assets."
    elif risk_score <= 5:
        risk_level = "MODERATE"
        interpretation = "Your portfolio has moderate risk. Consider monitoring for concentration issues."
    elif risk_score <= 7:
        risk_level = "ELEVATED"
        interpretation = "Your portfolio has elevated risk. You may want to consider rebalancing."
    else:
        risk_level = "HIGH"
        interpretation = "Your portfolio has high risk. Immediate attention may be needed."
    
    # Interpret individual factors
    volatility_assessment = "high" if volatility > 0.3 else "moderate" if volatility > 0.15 else "low"
    concentration_assessment = "high" if concentration > 0.4 else "moderate" if concentration > 0.2 else "low"
    correlation_assessment = "high" if correlation > 0.7 else "moderate" if correlation > 0.4 else "low"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "interpretation": interpretation,
        "volatility": {
            "value": round(volatility, 4),
            "assessment": volatility_assessment,
            "description": f"Portfolio volatility is {volatility_assessment} at {volatility*100:.1f}% annualized"
        },
        "concentration": {
            "value": round(concentration, 4),
            "assessment": concentration_assessment,
            "description": f"Portfolio concentration is {concentration_assessment} (HHI: {concentration:.3f})"
        },
        "correlation": {
            "value": round(correlation, 4),
            "assessment": correlation_assessment,
            "description": f"Asset correlation is {correlation_assessment} at {correlation:.2f}"
        }
    }


# Define the Risk Analyzer Agent
risk_analyzer_agent = LlmAgent(
    name="RiskAnalyzer",
    model="gemini-2.5-flash",
    description="Analyzes portfolio risk including volatility, concentration, and correlation metrics",
    instruction="""You are a professional portfolio risk analyst. Your task is to analyze the portfolio risk data provided and give a comprehensive risk assessment.

When analyzing risk:
1. Evaluate the overall risk score (1-10 scale, where 10 is highest risk)
2. Break down the contributing factors: volatility, concentration (HHI), and correlation
3. Provide actionable insights about what the risk metrics mean for the investor
4. Be clear and educational in your explanations, especially for beginner investors

Use the analyze_risk tool to process the portfolio data and generate your analysis.

Format your response as a structured JSON with:
- risk_score: The overall risk score (1-10)
- risk_level: LOW, MODERATE, ELEVATED, or HIGH
- interpretation: A brief explanation of what the risk level means
- volatility: Details about portfolio volatility
- concentration: Details about portfolio concentration
- correlation: Details about asset correlation
""",
    tools=[analyze_risk],
    output_key="risk_analysis"
)
