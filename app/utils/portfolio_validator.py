"""
Portfolio validation and CSV parsing utilities.
"""
import io
import csv
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import List


class Holding(BaseModel):
    """Single holding in a portfolio."""
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., ge=0, description="Purchase price per share")
    purchase_date: Optional[str] = Field(None, description="Purchase date (YYYY-MM-DD)")
    
    @validator('symbol')
    def uppercase_symbol(cls, v):
        return v.upper().strip()
    
    @validator('purchase_date')
    def validate_date(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class Portfolio(BaseModel):
    """Portfolio containing multiple holdings."""
    holdings: List[Holding] = Field(..., min_items=1, description="List of holdings")
    user_profile: str = Field("beginner", description="User profile: 'beginner' or 'senior'")
    
    @validator('user_profile')
    def validate_profile(cls, v):
        v = v.lower().strip()
        if v not in ["beginner", "senior", "intermediate"]:
            v = "beginner"
        return v


def validate_portfolio(portfolio_data: dict) -> tuple[bool, Optional[Portfolio], Optional[str]]:
    """
    Validate portfolio data structure.
    
    Args:
        portfolio_data: Dictionary with 'holdings' and optional 'user_profile'
        
    Returns:
        Tuple of (is_valid, parsed_portfolio, error_message)
    """
    try:
        portfolio = Portfolio(**portfolio_data)
        return True, portfolio, None
    except Exception as e:
        error_msg = str(e)
        # Make error message more user-friendly
        if "holdings" in error_msg.lower():
            error_msg = "Invalid holdings format. Each holding must have: symbol, quantity, purchase_price"
        return False, None, error_msg


def parse_csv_portfolio(csv_content: str) -> tuple[bool, list[dict], Optional[str]]:
    """
    Parse CSV content into portfolio holdings.
    
    Expected CSV format:
    Symbol,Quantity,Purchase_Price,Date
    AAPL,10,150.00,2024-01-15
    
    Args:
        csv_content: CSV file content as string
        
    Returns:
        Tuple of (is_valid, holdings_list, error_message)
    """
    try:
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_content))
        holdings = []
        row_num = 1  # Start from 1 for header
        
        for row in reader:
            row_num += 1
            
            # Try to find columns (case-insensitive)
            symbol = None
            quantity = None
            purchase_price = None
            purchase_date = None
            
            for key, value in row.items():
                key_lower = key.lower().strip()
                value = value.strip() if value else ""
                
                if "symbol" in key_lower or key_lower == "ticker":
                    symbol = value.upper()
                elif "quantity" in key_lower or key_lower == "shares" or key_lower == "qty":
                    try:
                        quantity = float(value)
                    except ValueError:
                        return False, [], f"Row {row_num}: Invalid quantity '{value}'"
                elif "price" in key_lower or key_lower == "purchase_price":
                    try:
                        # Remove currency symbols
                        value = value.replace("$", "").replace(",", "")
                        purchase_price = float(value)
                    except ValueError:
                        return False, [], f"Row {row_num}: Invalid price '{value}'"
                elif "date" in key_lower:
                    purchase_date = value if value else None
            
            # Validate required fields
            if not symbol:
                return False, [], f"Row {row_num}: Missing symbol"
            if quantity is None:
                return False, [], f"Row {row_num}: Missing quantity"
            if purchase_price is None:
                return False, [], f"Row {row_num}: Missing purchase price"
            
            holdings.append({
                "symbol": symbol,
                "quantity": quantity,
                "purchase_price": purchase_price,
                "purchase_date": purchase_date
            })
        
        if not holdings:
            return False, [], "CSV file is empty or has no valid data rows"
        
        return True, holdings, None
        
    except csv.Error as e:
        return False, [], f"CSV parsing error: {str(e)}"
    except Exception as e:
        return False, [], f"Error processing CSV: {str(e)}"


def get_csv_template() -> str:
    """
    Get CSV template for portfolio upload.
    
    Returns:
        CSV template string
    """
    return """Symbol,Quantity,Purchase_Price,Date
AAPL,10,150.00,2024-01-15
GOOGL,5,140.00,2024-02-20
MSFT,8,375.00,2024-03-10
"""


# Test portfolios for demo purposes
TEST_PORTFOLIOS = {
    "beginner": {
        "description": "Beginner Portfolio - Well Diversified with ETFs",
        "user_profile": "beginner",
        "holdings": [
            {"symbol": "SPY", "quantity": 20, "purchase_price": 450.00},
            {"symbol": "QQQ", "quantity": 10, "purchase_price": 380.00},
            {"symbol": "VTI", "quantity": 15, "purchase_price": 230.00},
        ]
    },
    "risky": {
        "description": "Risky Portfolio - Over-concentrated in Tech",
        "user_profile": "senior",
        "holdings": [
            {"symbol": "NVDA", "quantity": 50, "purchase_price": 480.00},
            {"symbol": "TSLA", "quantity": 5, "purchase_price": 240.00},
        ]
    },
    "balanced": {
        "description": "Balanced Portfolio - Good Mix of Stocks",
        "user_profile": "intermediate",
        "holdings": [
            {"symbol": "AAPL", "quantity": 15, "purchase_price": 185.00},
            {"symbol": "MSFT", "quantity": 10, "purchase_price": 370.00},
            {"symbol": "GOOGL", "quantity": 12, "purchase_price": 138.00},
            {"symbol": "AMZN", "quantity": 8, "purchase_price": 170.00},
            {"symbol": "META", "quantity": 6, "purchase_price": 315.00},
        ]
    }
}


def get_test_portfolio(portfolio_type: str) -> Optional[dict]:
    """
    Get a predefined test portfolio.
    
    Args:
        portfolio_type: One of 'beginner', 'risky', 'balanced'
        
    Returns:
        Portfolio dictionary or None if not found
    """
    return TEST_PORTFOLIOS.get(portfolio_type.lower())
