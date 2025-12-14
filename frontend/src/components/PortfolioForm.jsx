import { useState } from 'react'
import './PortfolioForm.css'

const AVAILABLE_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY', 'QQQ', 'VTI']

function PortfolioForm({ onSubmit, loading }) {
    const [holdings, setHoldings] = useState([
        { symbol: 'AAPL', quantity: 10, purchase_price: 150 }
    ])
    const [userProfile, setUserProfile] = useState('beginner')

    const addHolding = () => {
        setHoldings([...holdings, { symbol: '', quantity: 0, purchase_price: 0 }])
    }

    const removeHolding = (index) => {
        if (holdings.length > 1) {
            setHoldings(holdings.filter((_, i) => i !== index))
        }
    }

    const updateHolding = (index, field, value) => {
        const updated = [...holdings]
        if (field === 'symbol') {
            updated[index][field] = value.toUpperCase()
        } else {
            updated[index][field] = parseFloat(value) || 0
        }
        setHoldings(updated)
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        // Validate
        const validHoldings = holdings.filter(
            h => h.symbol && h.quantity > 0 && h.purchase_price >= 0
        )
        if (validHoldings.length === 0) {
            alert('Please add at least one valid holding')
            return
        }
        onSubmit({ holdings: validHoldings, user_profile: userProfile })
    }

    return (
        <form className="portfolio-form" onSubmit={handleSubmit}>
            <h2>Enter Your Portfolio</h2>

            <div className="form-group">
                <label>Investor Profile:</label>
                <select
                    value={userProfile}
                    onChange={(e) => setUserProfile(e.target.value)}
                >
                    <option value="beginner">🌱 Beginner</option>
                    <option value="intermediate">📈 Intermediate</option>
                    <option value="senior">🎯 Senior</option>
                </select>
            </div>

            <div className="holdings-list">
                <h3>Holdings</h3>
                {holdings.map((holding, index) => (
                    <div key={index} className="holding-row">
                        <div className="field">
                            <label>Symbol</label>
                            <input
                                type="text"
                                value={holding.symbol}
                                onChange={(e) => updateHolding(index, 'symbol', e.target.value)}
                                placeholder="AAPL"
                                list="stocks"
                                required
                            />
                            <datalist id="stocks">
                                {AVAILABLE_STOCKS.map(s => <option key={s} value={s} />)}
                            </datalist>
                        </div>
                        <div className="field">
                            <label>Quantity</label>
                            <input
                                type="number"
                                value={holding.quantity || ''}
                                onChange={(e) => updateHolding(index, 'quantity', e.target.value)}
                                placeholder="10"
                                min="0"
                                step="0.01"
                                required
                            />
                        </div>
                        <div className="field">
                            <label>Purchase Price ($)</label>
                            <input
                                type="number"
                                value={holding.purchase_price || ''}
                                onChange={(e) => updateHolding(index, 'purchase_price', e.target.value)}
                                placeholder="150.00"
                                min="0"
                                step="0.01"
                                required
                            />
                        </div>
                        {holdings.length > 1 && (
                            <button
                                type="button"
                                className="remove-btn"
                                onClick={() => removeHolding(index)}
                            >
                                ✕
                            </button>
                        )}
                    </div>
                ))}
            </div>

            <div className="form-actions">
                <button type="button" className="secondary-btn" onClick={addHolding}>
                    + Add Stock
                </button>
                <button type="submit" className="primary-btn" disabled={loading}>
                    {loading ? 'Analyzing...' : '🔍 Analyze Portfolio'}
                </button>
            </div>
        </form>
    )
}

export default PortfolioForm
