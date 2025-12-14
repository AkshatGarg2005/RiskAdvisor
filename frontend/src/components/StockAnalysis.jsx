// StockAnalysis - Individual stock risk ratings and Hold/Sell recommendations
import './StockAnalysis.css'

function StockAnalysis({ stockAnalysis }) {
    if (!stockAnalysis || !stockAnalysis.stock_analyses || stockAnalysis.stock_analyses.length === 0) {
        return null
    }

    const getRiskColor = (riskLevel) => {
        switch (riskLevel) {
            case 'LOW': return '#22c55e'
            case 'MODERATE': return '#f59e0b'
            case 'ELEVATED': return '#f97316'
            case 'HIGH': return '#ef4444'
            default: return '#6b7280'
        }
    }

    const getRecommendationBadge = (recommendation) => {
        switch (recommendation) {
            case 'HOLD': return { color: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)', icon: '✓' }
            case 'REDUCE': return { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', icon: '⚠' }
            case 'SELL': return { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', icon: '✗' }
            default: return { color: '#6b7280', bg: 'rgba(107, 114, 128, 0.1)', icon: '?' }
        }
    }

    return (
        <div className="stock-analysis-container">
            <div className="stock-analysis-header">
                <h3>📊 Individual Stock Analysis</h3>
                <div className="stock-summary">
                    <span className="summary-item">
                        <strong>{stockAnalysis.stock_count}</strong> Stocks
                    </span>
                    {stockAnalysis.high_risk_count > 0 && (
                        <span className="summary-item high-risk">
                            <strong>{stockAnalysis.high_risk_count}</strong> High Risk
                        </span>
                    )}
                    {stockAnalysis.sell_recommendations > 0 && (
                        <span className="summary-item sell">
                            <strong>{stockAnalysis.sell_recommendations}</strong> Action Needed
                        </span>
                    )}
                </div>
            </div>

            <div className="stock-cards">
                {stockAnalysis.stock_analyses.map((stock, index) => {
                    const badge = getRecommendationBadge(stock.recommendation)
                    return (
                        <div key={index} className={`stock-card ${stock.risk_level.toLowerCase()}`}>
                            <div className="stock-card-header">
                                <div className="stock-symbol">{stock.symbol}</div>
                                <div
                                    className="recommendation-badge"
                                    style={{ color: badge.color, backgroundColor: badge.bg }}
                                >
                                    {badge.icon} {stock.recommendation}
                                </div>
                            </div>

                            <div className="stock-metrics">
                                <div className="metric">
                                    <span className="metric-label">Value</span>
                                    <span className="metric-value">${stock.current_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                                </div>
                                <div className="metric">
                                    <span className="metric-label">Weight</span>
                                    <span className="metric-value">{stock.portfolio_weight?.toFixed(1)}%</span>
                                </div>
                                <div className="metric">
                                    <span className="metric-label">P/L</span>
                                    <span className={`metric-value ${stock.gain_loss_percent >= 0 ? 'positive' : 'negative'}`}>
                                        {stock.gain_loss_percent >= 0 ? '+' : ''}{stock.gain_loss_percent?.toFixed(1)}%
                                    </span>
                                </div>
                            </div>

                            <div className="risk-meter">
                                <div className="risk-bar-container">
                                    <div
                                        className="risk-bar"
                                        style={{
                                            width: `${stock.risk_score * 10}%`,
                                            backgroundColor: getRiskColor(stock.risk_level)
                                        }}
                                    />
                                </div>
                                <div className="risk-label">
                                    <span style={{ color: getRiskColor(stock.risk_level) }}>
                                        {stock.risk_level} RISK ({stock.risk_score}/10)
                                    </span>
                                </div>
                            </div>

                            {stock.reasons && stock.reasons.length > 0 && (
                                <div className="stock-reasons">
                                    {stock.reasons.map((reason, i) => (
                                        <div key={i} className="reason-item">• {reason}</div>
                                    ))}
                                </div>
                            )}

                            {stock.action && (
                                <div className="stock-action">
                                    <strong>Action:</strong> {stock.action}
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export default StockAnalysis
