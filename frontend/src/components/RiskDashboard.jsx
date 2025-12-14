import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    RadialBarChart,
    RadialBar,
    Legend
} from 'recharts'
import './RiskDashboard.css'
import StockAnalysis from './StockAnalysis'

const COLORS = ['#646cff', '#ff6b6b', '#4ecdc4', '#f9ca24', '#a55eea', '#26de81']

const getRiskColor = (score) => {
    if (score <= 3) return '#4ecdc4'
    if (score <= 5) return '#f9ca24'
    if (score <= 7) return '#ff9f43'
    return '#ff6b6b'
}

const getRiskLevel = (score) => {
    if (score <= 3) return 'LOW'
    if (score <= 5) return 'MODERATE'
    if (score <= 7) return 'ELEVATED'
    return 'HIGH'
}

function RiskDashboard({ data }) {
    if (!data) return null

    const riskScore = data.risk_score || 0
    const riskColor = getRiskColor(riskScore)
    const riskLevel = data.risk_level || data.risk_breakdown?.risk_level || getRiskLevel(riskScore)

    // Prepare chart data
    const riskBreakdownData = [
        { name: 'Volatility', value: (data.risk_breakdown?.volatility || 0) * 100, max: 100 },
        { name: 'Concentration', value: (data.risk_breakdown?.concentration || 0) * 100, max: 100 },
        { name: 'Correlation', value: (data.risk_breakdown?.correlation_risk || 0) * 100, max: 100 }
    ]

    // Radial chart data for risk score
    const riskGaugeData = [
        { name: 'Risk', value: riskScore * 10, fill: riskColor }
    ]

    return (
        <div className="risk-dashboard">
            <div className="dashboard-grid">
                {/* Risk Score Card */}
                <div className="card risk-score-card">
                    <h3>Overall Risk Score</h3>
                    <div className="risk-gauge">
                        <ResponsiveContainer width="100%" height={200}>
                            <RadialBarChart
                                cx="50%"
                                cy="50%"
                                innerRadius="60%"
                                outerRadius="100%"
                                barSize={20}
                                data={riskGaugeData}
                                startAngle={180}
                                endAngle={0}
                            >
                                <RadialBar
                                    dataKey="value"
                                    cornerRadius={10}
                                    background={{ fill: '#242451' }}
                                />
                            </RadialBarChart>
                        </ResponsiveContainer>
                        <div className="risk-score-value" style={{ color: riskColor }}>
                            <span className="score">{riskScore.toFixed(1)}</span>
                            <span className="label">/10</span>
                        </div>
                    </div>
                    <div className="risk-level" style={{ background: riskColor }}>
                        {riskLevel}
                    </div>
                    {data.risk_breakdown?.interpretation && (
                        <p className="interpretation">{data.risk_breakdown.interpretation}</p>
                    )}
                </div>

                {/* Risk Breakdown Chart */}
                <div className="card">
                    <h3>Risk Breakdown</h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={riskBreakdownData} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis type="number" domain={[0, 100]} stroke="#888" />
                            <YAxis dataKey="name" type="category" stroke="#888" width={100} />
                            <Tooltip
                                contentStyle={{ background: '#1a1a2e', border: 'none', borderRadius: '8px' }}
                            />
                            <Bar dataKey="value" fill="#646cff" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Portfolio Value */}
                <div className="card value-card">
                    <h3>Portfolio Value</h3>
                    <div className="big-number">
                        ${(data.total_value || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                    <p className="meta">ID: {data.portfolio_id}</p>
                    <p className="meta">Profile: {data.user_profile}</p>
                </div>

                {/* Risk Score Guide */}
                <div className="card risk-guide-card">
                    <h3>📊 Risk Score Guide</h3>
                    <div className="score-scale">
                        <div className="scale-item low">
                            <span className="range">1-3</span>
                            <span className="level">LOW</span>
                        </div>
                        <div className="scale-item moderate">
                            <span className="range">4-5</span>
                            <span className="level">MODERATE</span>
                        </div>
                        <div className="scale-item elevated">
                            <span className="range">6-7</span>
                            <span className="level">ELEVATED</span>
                        </div>
                        <div className="scale-item high">
                            <span className="range">8-10</span>
                            <span className="level">HIGH</span>
                        </div>
                    </div>

                    <div className="guide-sections">
                        <div className="ideal-score">
                            <h4>🎯 Target for {data.user_profile}</h4>
                            {data.user_profile === 'beginner' && <p>Aim for <span className="target-score">2-4</span></p>}
                            {data.user_profile === 'intermediate' && <p>Aim for <span className="target-score">4-6</span></p>}
                            {data.user_profile === 'senior' && <p>Aim for <span className="target-score">5-8</span></p>}
                            {!['beginner', 'intermediate', 'senior'].includes(data.user_profile) && <p>Aim for <span className="target-score">3-5</span></p>}
                        </div>

                        <div className="comparison-box">
                            <h4>👥 Your Standing</h4>
                            {riskScore <= 3 && <p><strong>Less risky than 75%</strong> of portfolios</p>}
                            {riskScore > 3 && riskScore <= 5 && <p><strong>In line with 60%</strong> of investors</p>}
                            {riskScore > 5 && riskScore <= 7 && <p><strong>Riskier than 70%</strong> of portfolios</p>}
                            {riskScore > 7 && <p><strong>Riskier than 90%</strong> of portfolios</p>}
                        </div>
                    </div>
                </div>
            </div>

            {/* Recommendations Section */}
            <div className="card recommendations-card">
                <h3>💡 AI Recommendations</h3>
                <div className="recommendations-list">
                    {(data.recommendations || []).map((rec, idx) => (
                        <div key={idx} className={`recommendation ${rec.action?.toLowerCase()}`}>
                            <div className="rec-header">
                                <span className={`action-badge ${rec.action?.toLowerCase()}`}>
                                    {rec.action}
                                </span>
                                <span className="stock">{rec.stock}</span>
                                {rec.confidence && (
                                    <span className="confidence">
                                        {Math.round(rec.confidence * 100)}% confident
                                    </span>
                                )}
                            </div>
                            <p className="reason">{rec.reason}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Scenarios Section */}
            <div className="card scenarios-card">
                <h3>🔮 What-If Scenarios</h3>
                <div className="scenarios-grid">
                    {(data.scenarios || []).map((scenario, idx) => (
                        <div key={idx} className={`scenario ${scenario.impact?.toLowerCase()}`}>
                            <h4>{scenario.scenario}</h4>
                            <div className="scenario-metrics">
                                <div className="metric">
                                    <span className="label">Current Risk</span>
                                    <span className="value">{scenario.current_risk_score?.toFixed(1)}</span>
                                </div>
                                <span className="arrow">→</span>
                                <div className="metric">
                                    <span className="label">New Risk</span>
                                    <span className="value" style={{ color: getRiskColor(scenario.new_risk_score) }}>
                                        {scenario.new_risk_score?.toFixed(1)}
                                    </span>
                                </div>
                            </div>
                            <p className="analysis">{scenario.analysis}</p>
                            <span className={`impact-badge ${scenario.impact?.toLowerCase()}`}>
                                {scenario.impact}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Alerts Section */}
            <div className="card alerts-card">
                <h3>🔔 Alerts</h3>
                <div className="alerts-list">
                    {(data.alerts || []).map((alert, idx) => (
                        <div key={idx} className={`alert ${alert.severity?.toLowerCase()}`}>
                            <div className="alert-header">
                                <span className={`severity-badge ${alert.severity?.toLowerCase()}`}>
                                    {alert.severity}
                                </span>
                                <span className="type">{alert.type}</span>
                            </div>
                            <p className="message">{alert.message}</p>
                            {alert.action && <p className="action">→ {alert.action}</p>}
                        </div>
                    ))}
                </div>
            </div>

            {/* Individual Stock Analysis */}
            {data.stock_analysis && (
                <StockAnalysis stockAnalysis={data.stock_analysis} />
            )}

            {/* Timestamp */}
            <p className="timestamp">Analysis generated: {new Date(data.timestamp).toLocaleString()}</p>
        </div>
    )
}

export default RiskDashboard
