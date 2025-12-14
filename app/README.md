# AI Investment Risk Scorer

A production-ready investment portfolio risk analysis system built with **Google ADK (Agent Development Kit)** and **FastAPI**.

## 🚀 Features

- **4 AI Agents** powered by Google ADK & Gemini 2.5 Flash:
  - **Risk Analyzer**: Calculates volatility, concentration (HHI), and correlation
  - **Recommendation Agent**: Personalized Buy/Hold/Sell advice
  - **Scenario Agent**: What-if portfolio modeling
  - **Alert Agent**: Rebalancing and tax-loss harvesting alerts

- **Multiple Input Methods**:
  - Manual portfolio entry via API
  - CSV file upload
  - Pre-built test portfolios

- **Cloud-Ready**: Dockerized for Google Cloud Run deployment

## 📁 Project Structure

```
app/
├── main.py                 # FastAPI application
├── agents/
│   ├── risk_analyzer_agent.py
│   ├── recommendation_agent.py
│   ├── scenario_agent.py
│   └── alert_agent.py
├── utils/
│   ├── price_fetcher.py    # Alpha Vantage integration
│   ├── calculations.py     # Risk calculations
│   └── portfolio_validator.py
├── Dockerfile
├── requirements.txt
├── .env                    # API keys (not in git)
└── .env.example
```

## 🛠️ Quick Start

### 1. Setup Environment

```bash
cd app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get test portfolio analysis
curl "http://localhost:8000/test-portfolio?type=beginner"

# Analyze custom portfolio
curl -X POST http://localhost:8000/analyze-portfolio \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "quantity": 10, "purchase_price": 150},
      {"symbol": "GOOGL", "quantity": 5, "purchase_price": 140}
    ],
    "user_profile": "beginner"
  }'
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze-portfolio` | POST | Analyze manual portfolio |
| `/upload-portfolio-csv` | POST | Analyze CSV portfolio |
| `/csv-template` | GET | Download CSV template |
| `/test-portfolio?type=` | GET | Get test portfolio (beginner/risky/balanced) |
| `/available-stocks` | GET | List stocks with mock data |

## 🐳 Docker Deployment

```bash
# Build image
docker build -t investment-risk-scorer .

# Run container
docker run -p 8000:8000 --env-file .env investment-risk-scorer
```

## ☁️ Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/investment-risk-scorer

# Deploy to Cloud Run
gcloud run deploy investment-risk-scorer \
  --image gcr.io/YOUR_PROJECT/investment-risk-scorer \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=your_key"
```

## 📈 Risk Calculation Formula

```
Risk_Score = (0.5 × Volatility) + (0.3 × Concentration) + (0.2 × Correlation)
```

Where:
- **Volatility**: Annualized standard deviation of returns
- **Concentration**: Herfindahl-Hirschman Index (HHI)
- **Correlation**: Average pairwise correlation between holdings
- Final score scaled to 1-10

## 🧪 Test Portfolios

| Type | Description |
|------|-------------|
| `beginner` | Well-diversified ETF portfolio (SPY, QQQ, VTI) |
| `risky` | Over-concentrated tech portfolio (NVDA, TSLA) |
| `balanced` | Mixed large-cap stocks (AAPL, MSFT, GOOGL, AMZN, META) |

## 📝 License

MIT License - Built for hackathon purposes.
