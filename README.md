<![CDATA[<div align="center">

# 🛡️ RiskAdvisor

### AI-Powered Investment Portfolio Risk Analysis

**Analyze, understand, and manage investment risk with a multi-agent AI system built on Google ADK & Gemini**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)](https://vite.dev)
[![Google ADK](https://img.shields.io/badge/Google_ADK-1.21+-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Firebase](https://img.shields.io/badge/Firebase-Auth_%26_Firestore-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

</div>

## 📖 Overview

**RiskAdvisor** is a full-stack investment portfolio risk analysis platform that leverages **7 specialized AI agents** orchestrated through the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and powered by **Gemini 2.5 Flash**. Users can input their stock holdings, and the system provides comprehensive risk scoring, actionable recommendations, what-if scenario modeling, real-time alerts, individual stock analysis, and an interactive AI chat assistant.

### ✨ Key Highlights

- **🤖 7 AI Agents** — Each agent handles a dedicated analysis domain (risk, recommendations, scenarios, alerts, stock analysis, portfolio chat, market analysis)
- **📊 Real-Time Data** — Live stock prices via Alpha Vantage API with intelligent mock fallback
- **💬 AI Chat Assistant** — Context-aware conversational interface for portfolio Q&A, what-if simulations, and market insights
- **🔐 Firebase Authentication** — Secure user accounts with Google sign-in and portfolio persistence via Firestore
- **📈 Interactive Dashboard** — Rich visualizations with risk gauges, allocation charts, and scenario comparisons using Recharts
- **☁️ Cloud-Ready** — Dockerized and deployable to Google Cloud Run

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │Portfolio  │ │   Risk    │ │  Stock   │ │   Chat Window     │  │
│  │  Form    │ │ Dashboard │ │ Analysis │ │  (AI Assistant)   │  │
│  └──────────┘ └───────────┘ └──────────┘ └───────────────────┘  │
│  ┌──────────┐ ┌───────────┐                                     │
│  │Auth Modal│ │  Saved    │    Firebase Auth + Firestore         │
│  │          │ │Portfolios │                                     │
│  └──────────┘ └───────────┘                                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────────┐
│                    Backend (FastAPI + Google ADK)                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Agent Orchestration Layer                   │    │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │  Risk    │ │Recommend- │ │ Scenario │ │  Alert   │  │    │
│  │  │ Analyzer │ │  ation    │ │  Agent   │ │  Agent   │  │    │
│  │  └──────────┘ └───────────┘ └──────────┘ └──────────┘  │    │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────────────────┐   │    │
│  │  │  Stock   │ │ Portfolio │ │   Market Analyzer    │   │    │
│  │  │ Analyzer │ │   Chat    │ │   (Web Search)       │   │    │
│  │  └──────────┘ └───────────┘ └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Utility Layer                          │    │
│  │  Price Fetcher │ Risk Calculations │ Portfolio Validator  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
         │                                       │
   Alpha Vantage API                    Google Gemini API
```

---

## 🤖 AI Agents

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| **Risk Analyzer** | Calculates portfolio volatility, concentration (HHI), and correlation risk | `analyze_risk` |
| **Recommendation** | Generates personalized Buy/Hold/Sell advice based on user profile | `generate_recommendations` |
| **Scenario** | Models what-if scenarios (market crash, selling positions, rebalancing) | `run_multiple_scenarios` |
| **Alert** | Detects rebalancing needs and tax-loss harvesting opportunities | `compile_all_alerts` |
| **Stock Analyzer** | Evaluates individual stocks with Hold/Sell recommendations using live data | `analyze_all_stocks` |
| **Portfolio Chat** | Context-aware Q&A with simulation tools (add/sell stocks, compare options) | `simulate_add_stock`, `simulate_sell_stock`, `compare_investment_options` |
| **Market Analyzer** | Web-search-powered market intelligence for price trends and news | Web search via Google |

---

## 📊 Risk Calculation

The composite risk score (1–10) is computed as:

```
Risk Score = (0.5 × Volatility) + (0.3 × Concentration) + (0.2 × Correlation)
```

| Component | Description |
|-----------|-------------|
| **Volatility** | Annualized standard deviation of returns |
| **Concentration** | Herfindahl-Hirschman Index (HHI) — measures portfolio diversification |
| **Correlation** | Average pairwise correlation between holdings |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & npm
- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/apikey)
- **Alpha Vantage API Key** *(optional, for live stock prices)* — [Get one here](https://www.alphavantage.co/support/#api-key)

### 1. Clone the Repository

```bash
git clone https://github.com/AkshatGarg2005/RiskAdvisor.git
cd RiskAdvisor
```

### 2. Backend Setup

```bash
cd app

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   GEMINI_API_KEY=your_gemini_key
#   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  (optional)
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# (Optional) Set API URL if backend isn't on localhost:8000
# Create a .env file with: VITE_API_URL=http://your-backend-url
```

### 4. Run the Application

**Start the backend:**
```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Start the frontend** (in a separate terminal):
```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173` (frontend) and `http://localhost:8000` (API).

---

## 📁 Project Structure

```
RiskAdvisor/
├── app/                              # Backend (Python/FastAPI)
│   ├── main.py                       # FastAPI application & API routes
│   ├── agents/                       # Google ADK AI agents
│   │   ├── risk_analyzer_agent.py    # Portfolio risk scoring
│   │   ├── recommendation_agent.py   # Buy/Hold/Sell recommendations
│   │   ├── scenario_agent.py         # What-if scenario modeling
│   │   ├── alert_agent.py            # Rebalancing & tax alerts
│   │   ├── stock_analyzer_agent.py   # Individual stock analysis
│   │   ├── chat_agent.py             # Conversational portfolio assistant
│   │   └── market_analyzer_agent.py  # Market intelligence (web search)
│   ├── utils/                        # Utility modules
│   │   ├── price_fetcher.py          # Alpha Vantage API + mock prices
│   │   ├── calculations.py           # Risk math (volatility, HHI, correlation)
│   │   └── portfolio_validator.py    # Input validation & CSV parsing
│   ├── Dockerfile                    # Docker container config
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variable template
│   └── .gitignore
│
├── frontend/                         # Frontend (React + Vite)
│   ├── src/
│   │   ├── App.jsx                   # Main app with tab navigation
│   │   ├── App.css                   # Global styles
│   │   ├── components/
│   │   │   ├── PortfolioForm.jsx     # Manual portfolio entry form
│   │   │   ├── RiskDashboard.jsx     # Risk analysis visualization
│   │   │   ├── StockAnalysis.jsx     # Individual stock recommendations
│   │   │   ├── ChatWindow.jsx        # AI chat assistant panel
│   │   │   ├── AuthModal.jsx         # Login/signup modal
│   │   │   └── SavedPortfolios.jsx   # Saved analysis management
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx       # Firebase auth state management
│   │   ├── services/
│   │   │   └── portfolioService.js   # Firestore save/load operations
│   │   └── firebase.js               # Firebase initialization
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── README.md                         # ← You are here
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | `GET` | API info and available endpoints |
| `/health` | `GET` | Health check |
| `/analyze-portfolio` | `POST` | Analyze a manually entered portfolio |
| `/upload-portfolio-csv` | `POST` | Analyze a portfolio from CSV file upload |
| `/csv-template` | `GET` | Download the CSV template |
| `/test-portfolio?type=` | `GET` | Run analysis on a test portfolio (`beginner`, `risky`, `balanced`) |
| `/available-stocks` | `GET` | List stocks with available price data |
| `/chat` | `POST` | AI chat about your portfolio |

### Example: Analyze a Portfolio

```bash
curl -X POST http://localhost:8000/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "quantity": 10, "purchase_price": 150.00},
      {"symbol": "GOOGL", "quantity": 5, "purchase_price": 140.00},
      {"symbol": "MSFT", "quantity": 8, "purchase_price": 380.00}
    ],
    "user_profile": "beginner"
  }'
```

### Example: CSV Upload

```bash
curl -X POST "http://localhost:8000/upload-portfolio-csv?user_profile=beginner" \
  -F "file=@portfolio.csv"
```

### Example: Chat with AI

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What if I add 20 shares of NVDA?",
    "portfolio_context": { "total_value": 50000, "risk_score": 5.2, "holdings": [] },
    "chat_history": []
  }'
```

---

## 🧪 Test Portfolios

Use pre-built portfolios to try the system without entering data:

| Type | Profile | Holdings | Description |
|------|---------|----------|-------------|
| `beginner` | Beginner | SPY, QQQ, VTI | Well-diversified ETF portfolio |
| `risky` | Senior | NVDA, TSLA | Over-concentrated tech/growth stocks |
| `balanced` | Beginner | AAPL, MSFT, GOOGL, AMZN, META | Mixed large-cap technology stocks |

```bash
# Try a test portfolio
curl http://localhost:8000/test-portfolio?type=balanced
```

---

## 🐳 Docker Deployment

```bash
cd app

# Build the image
docker build -t riskadvisor-api .

# Run the container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e ALPHA_VANTAGE_API_KEY=your_key \
  riskadvisor-api
```

## ☁️ Google Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/riskadvisor-api ./app

# Deploy to Cloud Run
gcloud run deploy riskadvisor-api \
  --image gcr.io/YOUR_PROJECT/riskadvisor-api \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=your_key,ALPHA_VANTAGE_API_KEY=your_key"
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI/LLM** | Google Gemini 2.5 Flash via Google ADK |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | React 19, Vite 7, Recharts |
| **Auth & DB** | Firebase Authentication, Cloud Firestore |
| **Market Data** | Alpha Vantage API |
| **Containerization** | Docker |
| **Cloud** | Google Cloud Run |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for AI agents |
| `ALPHA_VANTAGE_API_KEY` | ❌ | Alpha Vantage key for live stock prices (falls back to mock data) |
| `FIREBASE_PROJECT_ID` | ❌ | Firebase project ID (for server-side Firebase) |
| `GOOGLE_CLOUD_PROJECT_ID` | ❌ | GCP project ID (for Cloud Run deployment) |
| `PORT` | ❌ | Server port (default: `8000`) |

---

## 📝 License

This project is licensed under the MIT License. Built for hackathon purposes.
]]>
