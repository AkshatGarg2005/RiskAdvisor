"""
Portfolio risk calculation utilities.
Implements volatility, concentration (HHI), correlation, and overall risk scoring.
"""
import numpy as np
from typing import Optional


def calculate_returns(prices: list[float]) -> list[float]:
    """
    Calculate daily returns from a list of prices.
    
    Args:
        prices: List of historical prices (oldest to newest)
        
    Returns:
        List of daily returns (percentage changes)
    """
    if len(prices) < 2:
        return []
    
    prices_arr = np.array(prices)
    returns = np.diff(prices_arr) / prices_arr[:-1]
    return returns.tolist()


def calculate_volatility(prices: list[float]) -> float:
    """
    Calculate annualized volatility (standard deviation of returns).
    
    Args:
        prices: List of historical prices
        
    Returns:
        Annualized volatility as a decimal (e.g., 0.25 = 25%)
    """
    returns = calculate_returns(prices)
    if len(returns) < 2:
        return 0.0
    
    # Daily volatility
    daily_vol = np.std(returns)
    
    # Annualize (assuming 252 trading days)
    annualized_vol = daily_vol * np.sqrt(252)
    
    return float(annualized_vol)


def calculate_hhi(weights: list[float]) -> float:
    """
    Calculate Herfindahl-Hirschman Index for concentration risk.
    
    The HHI is the sum of squared weights, ranging from:
    - 1/n (perfectly diversified) to 1.0 (completely concentrated)
    
    Args:
        weights: List of portfolio weights (should sum to 1.0)
        
    Returns:
        HHI value between 0 and 1
    """
    if not weights:
        return 0.0
    
    weights_arr = np.array(weights)
    
    # Normalize weights to sum to 1
    total = weights_arr.sum()
    if total > 0:
        weights_arr = weights_arr / total
    else:
        return 0.0
    
    # Calculate HHI
    hhi = np.sum(weights_arr ** 2)
    
    return float(hhi)


def calculate_correlation(returns_matrix: list[list[float]]) -> float:
    """
    Calculate average pairwise correlation between asset returns.
    
    Args:
        returns_matrix: List of return series for each asset
        
    Returns:
        Average correlation coefficient (0 to 1)
    """
    if len(returns_matrix) < 2:
        return 0.0
    
    # Ensure all return series have the same length
    min_len = min(len(r) for r in returns_matrix if r)
    if min_len < 2:
        return 0.0
    
    # Trim returns to same length
    trimmed = [r[:min_len] for r in returns_matrix if r]
    if len(trimmed) < 2:
        return 0.0
    
    # Calculate correlation matrix
    returns_arr = np.array(trimmed)
    corr_matrix = np.corrcoef(returns_arr)
    
    # Handle NaN values
    corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)
    
    # Extract upper triangle (excluding diagonal)
    n = len(corr_matrix)
    upper_triangle = []
    for i in range(n):
        for j in range(i + 1, n):
            upper_triangle.append(abs(corr_matrix[i, j]))
    
    if not upper_triangle:
        return 0.0
    
    # Return average correlation
    avg_corr = np.mean(upper_triangle)
    
    return float(avg_corr)


def calculate_risk_score(
    volatility: float,
    concentration: float,
    correlation: float,
    weights: tuple[float, float, float] = (0.5, 0.3, 0.2)
) -> float:
    """
    Calculate overall risk score (1-10 scale).
    
    Formula: Risk = w1*Volatility + w2*Concentration + w3*Correlation
    Scaled to 1-10 range.
    
    Args:
        volatility: Annualized volatility (0-1+ scale)
        concentration: HHI concentration index (0-1 scale)
        correlation: Average correlation (0-1 scale)
        weights: Tuple of weights for (volatility, concentration, correlation)
        
    Returns:
        Risk score from 1 (lowest) to 10 (highest)
    """
    w_vol, w_conc, w_corr = weights
    
    # Normalize volatility to 0-1 scale (cap at 100% annual volatility)
    norm_volatility = min(volatility, 1.0)
    
    # Calculate weighted score (0-1 scale)
    raw_score = (
        w_vol * norm_volatility +
        w_conc * concentration +
        w_corr * correlation
    )
    
    # Scale to 1-10
    scaled_score = 1 + (raw_score * 9)
    
    # Clamp to valid range
    return round(max(1.0, min(10.0, scaled_score)), 2)


def analyze_portfolio_risk(enriched_holdings: list[dict]) -> dict:
    """
    Perform complete risk analysis on an enriched portfolio.
    
    Args:
        enriched_holdings: List of holdings with current_price and historical_prices
        
    Returns:
        Dictionary with comprehensive risk metrics
    """
    if not enriched_holdings:
        return {
            "risk_score": 0,
            "volatility": 0,
            "concentration": 0,
            "correlation_risk": 0,
            "error": "Empty portfolio"
        }
    
    # Calculate portfolio values and weights
    total_value = 0
    holdings_with_value = []
    
    for holding in enriched_holdings:
        current_price = holding.get("current_price", 0)
        quantity = holding.get("quantity", 0)
        value = current_price * quantity
        
        holdings_with_value.append({
            **holding,
            "value": value
        })
        total_value += value
    
    # Calculate weights
    weights = []
    for holding in holdings_with_value:
        if total_value > 0:
            weight = holding["value"] / total_value
        else:
            weight = 0
        holding["weight"] = weight
        weights.append(weight)
    
    # Calculate portfolio volatility (weighted average)
    individual_volatilities = []
    all_returns = []
    
    for holding in holdings_with_value:
        historical_prices = holding.get("historical_prices", [])
        if historical_prices:
            vol = calculate_volatility(historical_prices)
            individual_volatilities.append(vol * holding["weight"])
            returns = calculate_returns(historical_prices)
            if returns:
                all_returns.append(returns)
    
    portfolio_volatility = sum(individual_volatilities) if individual_volatilities else 0.0
    
    # Calculate concentration (HHI)
    concentration = calculate_hhi(weights)
    
    # Calculate correlation risk
    correlation_risk = calculate_correlation(all_returns)
    
    # Calculate overall risk score
    risk_score = calculate_risk_score(portfolio_volatility, concentration, correlation_risk)
    
    return {
        "risk_score": risk_score,
        "risk_breakdown": {
            "volatility": round(portfolio_volatility, 4),
            "concentration": round(concentration, 4),
            "correlation_risk": round(correlation_risk, 4)
        },
        "total_value": round(total_value, 2),
        "holdings_analysis": [
            {
                "symbol": h.get("symbol"),
                "value": round(h.get("value", 0), 2),
                "weight": round(h.get("weight", 0) * 100, 2),
                "individual_volatility": round(
                    calculate_volatility(h.get("historical_prices", [])), 4
                )
            }
            for h in holdings_with_value
        ]
    }
