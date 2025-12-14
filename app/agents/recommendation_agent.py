"""
Recommendation Agent using Google ADK.
Profiles user and generates actionable Buy/Hold/Sell recommendations.
"""
import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_recommendations(
    portfolio_data: str,
    user_profile: str,
    risk_score: float,
    concentration_data: str
) -> dict:
    """
    Generate personalized investment recommendations based on portfolio analysis.
    
    Args:
        portfolio_data: JSON string of portfolio holdings with values and weights
        user_profile: User profile type ('beginner', 'intermediate', 'senior')
        risk_score: Overall portfolio risk score (1-10)
        concentration_data: JSON string with sector/stock concentration details
        
    Returns:
        Dictionary with personalized recommendations
    """
    recommendations = []
    
    # Parse risk level
    is_high_risk = risk_score > 6
    is_beginner = user_profile.lower() == "beginner"
    
    # Generate base recommendations based on profile and risk
    if is_beginner:
        if is_high_risk:
            recommendations.append({
                "action": "BUY",
                "stock": "SPY",
                "reason": "Add index fund exposure to reduce overall portfolio risk through diversification",
                "confidence": 0.92,
                "priority": "HIGH"
            })
            recommendations.append({
                "action": "HOLD",
                "stock": "Current Holdings",
                "reason": "Avoid panic selling; focus on gradual rebalancing instead",
                "confidence": 0.85,
                "priority": "MEDIUM"
            })
        else:
            recommendations.append({
                "action": "HOLD",
                "stock": "Current Holdings",
                "reason": "Your portfolio is well-balanced. Continue your current investment strategy.",
                "confidence": 0.90,
                "priority": "MEDIUM"
            })
            recommendations.append({
                "action": "BUY",
                "stock": "VTI",
                "reason": "Consider adding total market ETF for long-term growth",
                "confidence": 0.78,
                "priority": "LOW"
            })
    else:  # Intermediate or Senior
        if is_high_risk:
            recommendations.append({
                "action": "SELL",
                "stock": "Largest Holding",
                "reason": "Consider reducing position size to decrease concentration risk",
                "confidence": 0.88,
                "priority": "HIGH"
            })
            recommendations.append({
                "action": "BUY",
                "stock": "Sector ETF",
                "reason": "Replace individual stock exposure with sector ETF to maintain exposure while reducing single-stock risk",
                "confidence": 0.82,
                "priority": "MEDIUM"
            })
        else:
            recommendations.append({
                "action": "HOLD",
                "stock": "Current Holdings",
                "reason": "Portfolio risk is within acceptable bounds. Review quarterly.",
                "confidence": 0.88,
                "priority": "MEDIUM"
            })
    
    # Add general recommendation
    recommendations.append({
        "action": "REVIEW",
        "stock": "Portfolio",
        "reason": "Schedule quarterly portfolio review to assess performance and rebalance if needed",
        "confidence": 0.95,
        "priority": "MEDIUM"
    })
    
    return {
        "user_profile": user_profile,
        "profile_description": "Beginner investor - focus on safety and education" if is_beginner else "Experienced investor - can tolerate higher risk",
        "recommendations": recommendations[:5],  # Limit to 5 recommendations
        "general_advice": get_advice_for_profile(user_profile, risk_score)
    }


def get_advice_for_profile(profile: str, risk_score: float) -> str:
    """Get general advice based on user profile and risk level."""
    if profile.lower() == "beginner":
        if risk_score > 6:
            return "As a beginner, your current portfolio may be too risky. Consider shifting 20-30% to index funds."
        return "Great job maintaining a balanced portfolio! Keep learning about different asset classes."
    elif profile.lower() == "senior":
        if risk_score > 7:
            return "While you may have appetite for risk, ensure you have adequate stop-losses in place."
        return "Your portfolio management is solid. Consider tax-loss harvesting opportunities."
    else:
        return "Review your portfolio quarterly and consider your long-term financial goals."


# Define the Recommendation Agent
recommendation_agent = LlmAgent(
    name="RecommendationAgent",
    model="gemini-2.5-flash",
    description="Generates personalized investment recommendations based on user profile and portfolio analysis",
    instruction="""You are a personalized investment advisor. Your role is to analyze the portfolio and provide actionable recommendations tailored to the investor's experience level.

For each portfolio:
1. Consider the user profile (beginner, intermediate, senior investor)
2. Evaluate the current risk level and concentration
3. Generate 3-5 specific, actionable recommendations
4. Each recommendation should include: action (BUY/HOLD/SELL), specific stock/ETF, reason, and confidence level

Be especially careful with beginners:
- Avoid recommending complex strategies
- Focus on diversification and safety
- Educate while advising

For senior investors:
- Can suggest more sophisticated strategies
- Consider tax implications
- Focus on optimization rather than basics

Use the generate_recommendations tool to create personalized advice.
""",
    tools=[generate_recommendations],
    output_key="recommendations"
)
