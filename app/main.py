"""
AI Investment Risk Scorer - FastAPI Backend with Google ADK
Main application with multi-agent orchestration for portfolio analysis.
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Google ADK imports
from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Local imports
from utils.price_fetcher import enrich_portfolio_with_prices, MOCK_PRICES
from utils.calculations import analyze_portfolio_risk
from utils.portfolio_validator import (
    validate_portfolio,
    parse_csv_portfolio,
    get_csv_template,
    get_test_portfolio,
    TEST_PORTFOLIOS,
    Holding,
    Portfolio
)
from agents.risk_analyzer_agent import risk_analyzer_agent, analyze_risk
from agents.recommendation_agent import recommendation_agent, generate_recommendations
from agents.scenario_agent import scenario_agent, run_multiple_scenarios
from agents.alert_agent import alert_agent, compile_all_alerts
from agents.chat_agent import portfolio_chat_agent, get_portfolio_summary
from agents.stock_analyzer_agent import stock_analyzer_agent, analyze_all_stocks
from agents.market_analyzer_agent import market_analyzer_agent

# Load environment variables
load_dotenv()

# Configure API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


# Request/Response Models
class HoldingRequest(BaseModel):
    symbol: str = Field(..., min_length=1, description="Stock ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., ge=0, description="Purchase price per share")
    purchase_date: Optional[str] = Field(None, description="Purchase date (YYYY-MM-DD)")


class PortfolioRequest(BaseModel):
    holdings: list[HoldingRequest] = Field(..., min_items=1)
    user_profile: str = Field("beginner", description="User profile: 'beginner' or 'senior'")


class AnalysisResponse(BaseModel):
    portfolio_id: str
    user_profile: str
    risk_score: float
    risk_breakdown: dict
    recommendations: list
    scenarios: list
    alerts: list
    timestamp: str
    total_value: float
    holdings: list = []  # Enriched holdings data for chat context
    stock_analysis: dict = {}  # Individual stock risk analysis with Hold/Sell recommendations


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    print("🚀 Investment Risk Scorer API starting up...")
    print(f"📊 Loaded {len(MOCK_PRICES)} stock symbols for testing")
    yield
    print("👋 Investment Risk Scorer API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AI Investment Risk Scorer",
    description="Multi-agent portfolio analysis using Google ADK",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize session service for ADK
session_service = InMemorySessionService()

# Create the ADK Runner
runner = Runner(
    app_name="investment_risk_scorer",
    agent=risk_analyzer_agent,  # We'll switch agents per call
    session_service=session_service
)


async def run_single_agent(agent: LlmAgent, user_message: str, session_id: str) -> dict:
    """
    Run a single agent using the ADK Runner and collect results.
    
    Args:
        agent: The LlmAgent to run
        user_message: The prompt/context to send to the agent
        session_id: Unique session ID for this run
        
    Returns:
        Dictionary with agent response
    """
    from google.genai import types
    
    # Create a runner for this specific agent
    agent_runner = Runner(
        app_name="investment_risk_scorer",
        agent=agent,
        session_service=session_service
    )
    
    try:
        # Create or get session
        session = await session_service.get_session(
            app_name="investment_risk_scorer",
            user_id="default_user",
            session_id=session_id
        )
        
        if not session:
            session = await session_service.create_session(
                app_name="investment_risk_scorer",
                user_id="default_user",
                session_id=session_id
            )
        
        # Run the agent and collect all events
        final_response = ""
        function_results = []
        all_events = []
        
        async for event in agent_runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        ):
            all_events.append(event)
            
            # Collect text responses
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Capture text parts
                    if hasattr(part, 'text') and part.text:
                        final_response += part.text
            
            # Capture function responses using ADK's method
            try:
                func_responses = event.get_function_responses()
                if func_responses:
                    for func_resp in func_responses:
                        function_results.append({
                            "name": getattr(func_resp, 'name', 'unknown'),
                            "response": func_resp.response if hasattr(func_resp, 'response') else None
                        })
            except Exception as e:
                # Fallback: try to capture from parts directly
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'function_response') and part.function_response:
                            try:
                                func_resp = part.function_response
                                function_results.append({
                                    "name": getattr(func_resp, 'name', 'unknown'),
                                    "response": func_resp.response if hasattr(func_resp, 'response') else None
                                })
                            except:
                                pass
        
        # Try to get output from session state (output_key)
        session_output = None
        try:
            updated_session = await session_service.get_session(
                app_name="investment_risk_scorer",
                user_id="default_user",
                session_id=session_id
            )
            if updated_session and hasattr(updated_session, 'state'):
                session_output = dict(updated_session.state) if updated_session.state else None
        except Exception as e:
            print(f"Error getting session state: {e}")
        
        return {
            "success": True,
            "response": final_response,
            "function_results": function_results,
            "session_output": session_output,
            "agent_name": agent.name,
            "events_count": len(all_events)
        }
        
    except Exception as e:
        import traceback
        print(f"Agent {agent.name} error: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "agent_name": agent.name
        }


async def run_agent_analysis(portfolio_data: dict, user_profile: str) -> dict:
    """
    Run all agents using the ADK Runner to actually invoke Gemini API.
    
    This uses the ADK Runner to execute each agent, which will:
    1. Send the prompt to Gemini
    2. Allow Gemini to decide whether to call tools
    3. Execute tools if needed
    4. Return the LLM-generated response
    """
    import uuid
    
    # Enrich portfolio with current prices
    enriched_holdings = enrich_portfolio_with_prices(
        portfolio_data.get("holdings", []),
        use_mock=False  # Use real Alpha Vantage API data
    )
    
    # Calculate base risk metrics (for context)
    risk_analysis = analyze_portfolio_risk(enriched_holdings)
    
    # Prepare portfolio context for agents
    portfolio_json = json.dumps({
        "holdings": enriched_holdings,
        "total_value": risk_analysis.get("total_value", 0),
        "holdings_analysis": risk_analysis.get("holdings_analysis", [])
    }, indent=2)
    
    # Find largest holding for context
    holdings_analysis = risk_analysis.get("holdings_analysis", [])
    largest_holding = max(holdings_analysis, key=lambda x: x.get("value", 0)) if holdings_analysis else {"symbol": "N/A", "value": 0}
    
    # Create unique session IDs for each agent
    base_session_id = str(uuid.uuid4())[:8]
    
    # Prepare prompts for each agent
    risk_prompt = f"""Analyze this portfolio for risk:

Portfolio Data:
{portfolio_json}

Pre-calculated Risk Metrics:
- Volatility: {risk_analysis.get("risk_breakdown", {}).get("volatility", 0):.4f}
- Concentration (HHI): {risk_analysis.get("risk_breakdown", {}).get("concentration", 0):.4f}
- Correlation Risk: {risk_analysis.get("risk_breakdown", {}).get("correlation_risk", 0):.4f}
- Base Risk Score: {risk_analysis.get("risk_score", 0):.2f}

Use the analyze_risk tool to generate a comprehensive risk assessment."""

    recommendation_prompt = f"""Generate investment recommendations for this portfolio:

Portfolio Data:
{portfolio_json}

User Profile: {user_profile}
Current Risk Score: {risk_analysis.get("risk_score", 0):.2f}
Largest Holding: {largest_holding.get("symbol", "N/A")} (${largest_holding.get("value", 0):,.2f})

Use the generate_recommendations tool to provide personalized advice."""

    scenario_prompt = f"""Model what-if scenarios for this portfolio:

Portfolio Value: ${risk_analysis.get("total_value", 0):,.2f}
Current Risk Score: {risk_analysis.get("risk_score", 0):.2f}
Largest Holding: {largest_holding.get("symbol", "N/A")} valued at ${largest_holding.get("value", 0):,.2f}

Use the run_multiple_scenarios tool to show how different actions would affect the portfolio."""

    alert_prompt = f"""Check this portfolio for alerts:

Portfolio Data:
{portfolio_json}

User Profile: {user_profile}

Use the compile_all_alerts tool to generate rebalancing and tax-loss harvesting alerts."""

    # Run all agents (can be parallelized in production)
    print("🤖 Running Risk Analyzer Agent with Gemini...")
    risk_result = await run_single_agent(
        risk_analyzer_agent, 
        risk_prompt, 
        f"{base_session_id}_risk"
    )
    
    print("🤖 Running Recommendation Agent with Gemini...")
    recommendation_result = await run_single_agent(
        recommendation_agent, 
        recommendation_prompt, 
        f"{base_session_id}_rec"
    )
    
    print("🤖 Running Scenario Agent with Gemini...")
    scenario_result = await run_single_agent(
        scenario_agent, 
        scenario_prompt, 
        f"{base_session_id}_scenario"
    )
    
    print("🤖 Running Alert Agent with Gemini...")
    alert_result = await run_single_agent(
        alert_agent, 
        alert_prompt, 
        f"{base_session_id}_alert"
    )
    
    # Parse responses - use fallback tool results but enrich with Gemini's text response
    def parse_agent_response(result, fallback_tool_result, output_key=None):
        """
        Use fallback tool result as structured data, enriched with Gemini's interpretation.
        
        The ADK event capture is not reliably extracting function results,
        so we use the fallback (direct tool calls) for structured data
        while preserving Gemini's natural language response for context.
        """
        if not fallback_tool_result:
            return {}
            
        # Get Gemini's text response if available
        gemini_text = ""
        if result.get("success"):
            gemini_text = result.get("response", "")
        
        # If fallback is a dict, add gemini's interpretation
        if isinstance(fallback_tool_result, dict) and gemini_text.strip():
            fallback_tool_result["gemini_response"] = gemini_text
        
        return fallback_tool_result
    
    # Get fallback results from direct tool calls
    fallback_risk = analyze_risk(
        portfolio_data=portfolio_json,
        volatility=risk_analysis.get("risk_breakdown", {}).get("volatility", 0),
        concentration=risk_analysis.get("risk_breakdown", {}).get("concentration", 0),
        correlation=risk_analysis.get("risk_breakdown", {}).get("correlation_risk", 0),
        risk_score=risk_analysis.get("risk_score", 0)
    )
    
    fallback_recommendations = generate_recommendations(
        portfolio_data=portfolio_json,
        user_profile=user_profile,
        risk_score=risk_analysis.get("risk_score", 0),
        concentration_data=json.dumps(largest_holding)
    )
    
    fallback_scenarios = run_multiple_scenarios(
        portfolio_value=risk_analysis.get("total_value", 0),
        risk_score=risk_analysis.get("risk_score", 0),
        largest_holding=largest_holding.get("symbol", "N/A"),
        largest_holding_value=largest_holding.get("value", 0)
    )
    
    fallback_alerts = compile_all_alerts(
        portfolio_data=portfolio_json,
        user_profile=user_profile
    )
    
    # Run individual stock analysis (uses Alpha Vantage with mock fallback)
    print("🤖 Running Stock Analyzer for individual stock recommendations...")
    stock_analysis_result = analyze_all_stocks(risk_analysis.get("holdings_analysis", []))
    
    return {
        "risk_analysis": parse_agent_response(risk_result, fallback_risk, "risk_analysis"),
        "recommendations": parse_agent_response(recommendation_result, fallback_recommendations, "recommendations"),
        "scenarios": parse_agent_response(scenario_result, fallback_scenarios, "scenarios"),
        "alerts": parse_agent_response(alert_result, fallback_alerts, "alerts"),
        "stock_analysis": stock_analysis_result,  # Individual stock risk and recommendations
        "base_analysis": risk_analysis,
        "gemini_responses": {
            "risk": risk_result,
            "recommendations": recommendation_result,
            "scenarios": scenario_result,
            "alerts": alert_result
        }
    }


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Investment Risk Scorer",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "POST /analyze-portfolio",
            "upload_csv": "POST /upload-portfolio-csv",
            "csv_template": "GET /csv-template",
            "test_portfolios": "GET /test-portfolio?type=beginner|risky|balanced"
        }
    }


@app.post("/analyze-portfolio", response_model=AnalysisResponse)
async def analyze_portfolio(portfolio: PortfolioRequest):
    """
    Analyze a manually entered portfolio.
    
    Runs 4 AI agents in parallel:
    - Risk Analyzer: Calculate volatility, concentration, correlation
    - Recommendation Agent: Generate Buy/Hold/Sell advice
    - Scenario Agent: Model what-if scenarios
    - Alert Agent: Check for rebalancing and tax opportunities
    """
    try:
        # Convert to dict
        portfolio_data = {
            "holdings": [h.model_dump() for h in portfolio.holdings],
            "user_profile": portfolio.user_profile
        }
        
        # Run agent analysis
        results = await run_agent_analysis(portfolio_data, portfolio.user_profile)
        
        # Helper to safely get from dict or return default
        def safe_get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return default
        
        # Construct response
        base_analysis = results.get("base_analysis", {})
        risk_result = results.get("risk_analysis", {})
        recommendations = results.get("recommendations", {})
        scenarios = results.get("scenarios", {})
        alerts = results.get("alerts", {})
        
        portfolio_id = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        response = AnalysisResponse(
            portfolio_id=portfolio_id,
            user_profile=portfolio.user_profile,
            risk_score=safe_get(risk_result, "risk_score", base_analysis.get("risk_score", 0)),
            risk_breakdown={
                "volatility": base_analysis.get("risk_breakdown", {}).get("volatility", 0),
                "concentration": base_analysis.get("risk_breakdown", {}).get("concentration", 0),
                "correlation_risk": base_analysis.get("risk_breakdown", {}).get("correlation_risk", 0),
                "risk_level": safe_get(risk_result, "risk_level", "UNKNOWN"),
                "interpretation": safe_get(risk_result, "interpretation", "")
            },
            recommendations=safe_get(recommendations, "recommendations", []),
            scenarios=safe_get(scenarios, "scenarios", []),
            alerts=safe_get(alerts, "alerts", []),
            timestamp=datetime.now().isoformat(),
            total_value=base_analysis.get("total_value", 0),
            holdings=base_analysis.get("holdings_analysis", []),
            stock_analysis=results.get("stock_analysis", {})  # Individual stock risk & recommendations
        )
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/upload-portfolio-csv")
async def upload_portfolio_csv(
    file: UploadFile = File(...),
    user_profile: str = Query("beginner", description="User profile")
):
    """
    Analyze a portfolio uploaded via CSV file.
    
    Expected CSV format:
    Symbol,Quantity,Purchase_Price,Date
    AAPL,10,150.00,2024-01-15
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode("utf-8")
        
        # Parse CSV
        is_valid, holdings, error = parse_csv_portfolio(csv_content)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"CSV parsing error: {error}")
        
        # Create portfolio request and analyze
        portfolio_data = {
            "holdings": holdings,
            "user_profile": user_profile
        }
        
        # Run agent analysis
        results = await run_agent_analysis(portfolio_data, user_profile)
        
        # Helper to safely get from dict or return default
        def safe_get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return default
        
        # Construct response
        base_analysis = results.get("base_analysis", {})
        risk_result = results.get("risk_analysis", {})
        recommendations = results.get("recommendations", {})
        scenarios = results.get("scenarios", {})
        alerts = results.get("alerts", {})
        
        portfolio_id = f"csv_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        response = {
            "portfolio_id": portfolio_id,
            "user_profile": user_profile,
            "risk_score": safe_get(risk_result, "risk_score", base_analysis.get("risk_score", 0)),
            "risk_breakdown": {
                "volatility": base_analysis.get("risk_breakdown", {}).get("volatility", 0),
                "concentration": base_analysis.get("risk_breakdown", {}).get("concentration", 0),
                "correlation_risk": base_analysis.get("risk_breakdown", {}).get("correlation_risk", 0),
                "risk_level": safe_get(risk_result, "risk_level", "UNKNOWN"),
                "interpretation": safe_get(risk_result, "interpretation", "")
            },
            "recommendations": safe_get(recommendations, "recommendations", []),
            "scenarios": safe_get(scenarios, "scenarios", []),
            "alerts": safe_get(alerts, "alerts", []),
            "timestamp": datetime.now().isoformat(),
            "total_value": base_analysis.get("total_value", 0),
            "holdings": base_analysis.get("holdings_analysis", []),  # Include enriched holdings
            "stock_analysis": results.get("stock_analysis", {}),  # Individual stock risk & recommendations
            "holdings_parsed": len(holdings)
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV upload failed: {str(e)}")


@app.get("/csv-template")
async def get_csv_template_endpoint():
    """Download CSV template for portfolio upload."""
    template = get_csv_template()
    return PlainTextResponse(
        content=template,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=portfolio_template.csv"}
    )


@app.get("/test-portfolio")
async def get_test_portfolio_endpoint(
    type: str = Query("beginner", description="Portfolio type: beginner, risky, balanced")
):
    """
    Get a predefined test portfolio for demo purposes.
    Useful for avoiding API rate limits during testing.
    """
    portfolio = get_test_portfolio(type)
    
    if not portfolio:
        available = list(TEST_PORTFOLIOS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Portfolio type '{type}' not found. Available: {available}"
        )
    
    # Run analysis on test portfolio
    results = await run_agent_analysis(portfolio, portfolio.get("user_profile", "beginner"))
    
    # Helper to safely get from dict or return default
    def safe_get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default
    
    base_analysis = results.get("base_analysis", {})
    risk_result = results.get("risk_analysis", {})
    recommendations = results.get("recommendations", {})
    scenarios = results.get("scenarios", {})
    alerts = results.get("alerts", {})
    
    return {
        "portfolio_type": type,
        "description": portfolio.get("description", ""),
        "portfolio_id": f"test_{type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_profile": portfolio.get("user_profile", "beginner"),
        "holdings": portfolio.get("holdings", []),
        "risk_score": safe_get(risk_result, "risk_score", base_analysis.get("risk_score", 0)),
        "risk_level": safe_get(risk_result, "risk_level", "UNKNOWN"),
        "interpretation": safe_get(risk_result, "interpretation", ""),
        "risk_breakdown": base_analysis.get("risk_breakdown", {}),
        "recommendations": safe_get(recommendations, "recommendations", []),
        "scenarios": safe_get(scenarios, "scenarios", []),
        "alerts": safe_get(alerts, "alerts", []),
        "timestamp": datetime.now().isoformat(),
        "total_value": base_analysis.get("total_value", 0),
        "gemini_used": True,
        "gemini_raw_responses": {
            "risk": results.get("gemini_responses", {}).get("risk", {}),
            "recommendations": results.get("gemini_responses", {}).get("recommendations", {}),
            "scenarios": results.get("gemini_responses", {}).get("scenarios", {}),
            "alerts": results.get("gemini_responses", {}).get("alerts", {})
        }
    }


@app.get("/available-stocks")
async def get_available_stocks():
    """Get list of stocks available for demo (mock data)."""
    return {
        "stocks": list(MOCK_PRICES.keys()),
        "note": "These stocks have mock price data for demo purposes"
    }


# Chat Request Model
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's question")
    portfolio_context: dict = Field(..., description="Current portfolio analysis data")
    chat_history: list = Field(default=[], description="Last 15 messages for conversation context")


@app.post("/chat")
async def chat_with_portfolio(request: ChatRequest):
    """
    Chat endpoint using Google ADK Runner.
    The agent can call tools for calculations, processed by Gemini.
    """
    from agents.chat_agent import portfolio_chat_agent, get_portfolio_summary
    from google.genai import types
    import uuid
    
    try:
        # Validate message
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get portfolio values for context
        portfolio_value = request.portfolio_context.get('total_value', 0)
        risk_score = request.portfolio_context.get('risk_score', 5)
        risk_level = request.portfolio_context.get('risk_level', 'UNKNOWN')
        holdings = request.portfolio_context.get('holdings', [])
        
        # Debug: Log portfolio context keys and holdings
        print(f"💬 Chat question (ADK): {request.message}")
        print(f"📊 Portfolio context keys: {list(request.portfolio_context.keys())}")
        print(f"📊 Portfolio: ${portfolio_value:,.2f}, Risk: {risk_score}, Holdings count: {len(holdings)}")
        if holdings:
            print(f"💼 First holding sample: {holdings[0] if holdings else 'None'}")
        print(f"📜 Chat history: {len(request.chat_history)} messages")
        
        # Detect if this is a market analysis question
        market_keywords = [
            "market", "going to rise", "going to fall", "will rise", "will fall",
            "stock price", "forecast", "prediction", "next week", "next month",
            "trend", "outlook", "bullish", "bearish", "crash", "rally",
            "news", "analyst", "sentiment", "future", "going up", "going down"
        ]
        message_lower = request.message.lower()
        is_market_question = any(keyword in message_lower for keyword in market_keywords)
        
        # Create portfolio summary for context
        portfolio_summary = get_portfolio_summary(request.portfolio_context)
        
        # Format chat history for context
        history_text = ""
        if request.chat_history:
            history_parts = []
            for msg in request.chat_history[-15:]:  # Last 15 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if content:
                    prefix = "User" if role == 'user' else "Assistant"
                    history_parts.append(f"{prefix}: {content}")
            if history_parts:
                history_text = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(history_parts) + "\n"
        
        # Build the prompt with portfolio context and history injected
        user_message = f"""Here is the user's current portfolio data:

{portfolio_summary}

KEY VALUES FOR CALCULATIONS:
- current_portfolio_value: {portfolio_value}
- current_risk_score: {risk_score}
- risk_level: {risk_level}
- holdings_count: {len(holdings)}
{history_text}
User's current question: {request.message}

If the user asks about buying/adding stocks or what-if scenarios, USE the simulate_add_stock tool with the values above.
If they ask about selling, USE simulate_sell_stock.
If they ask to compare options, USE compare_investment_options.
Use conversation history for context when answering follow-up questions.
Always use the tools for calculations - don't estimate manually."""

        # Create unique session for this chat
        session_id = f"chat_{uuid.uuid4().hex[:8]}"
        
        # Choose agent based on question type
        if is_market_question:
            print(f"📈 Detected MARKET question - using MarketAnalyzer with web search...")
            selected_agent = market_analyzer_agent
            agent_type = "market"
            # For market questions, simplify the message
            user_message = f"""User question about market/stocks: {request.message}

Search the web for latest news and data, then provide analysis with sources.
If the question mentions a specific stock, get the live price first."""
        else:
            print(f"🤖 Running Portfolio Chat Agent with ADK...")
            selected_agent = portfolio_chat_agent
            agent_type = "portfolio"
        
        # Run the agent using ADK Runner
        agent_runner = Runner(
            app_name="investment_risk_scorer",
            agent=selected_agent,
            session_service=session_service
        )
        
        # Create session
        session = await session_service.create_session(
            app_name="investment_risk_scorer",
            user_id="chat_user",
            session_id=session_id
        )
        
        # Run agent and collect response
        final_response = ""
        tool_calls = []
        tool_results = []
        
        async for event in agent_runner.run_async(
            user_id="chat_user",
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        ):
            # Collect text responses
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_response += part.text
                    # Track function calls
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_calls.append({
                            "name": part.function_call.name,
                            "args": dict(part.function_call.args) if part.function_call.args else {}
                        })
            
            # Capture function responses
            try:
                func_responses = event.get_function_responses()
                if func_responses:
                    for func_resp in func_responses:
                        tool_results.append({
                            "name": getattr(func_resp, 'name', 'unknown'),
                            "response": func_resp.response if hasattr(func_resp, 'response') else None
                        })
            except:
                pass
        
        print(f"✅ ADK Chat response generated")
        print(f"🔧 Tool calls: {len(tool_calls)}, Tool results: {len(tool_results)}")
        
        return {
            "success": True,
            "answer": final_response,
            "question": request.message,
            "adk_used": True,
            "agent_type": agent_type,  # "market" or "portfolio"
            "tool_calls": tool_calls,
            "tool_results": tool_results
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "answer": "I'm sorry, I couldn't process your question. Please try again.",
            "adk_used": True
        }


# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
