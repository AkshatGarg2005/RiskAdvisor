// Saved Portfolios - Display and manage saved portfolio analyses
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getUserAnalyses, updateAnalysis, deleteAnalysis } from '../services/portfolioService'
import './SavedPortfolios.css'

function SavedPortfolios({ onLoadAnalysis }) {
    const [analyses, setAnalyses] = useState([])
    const [loading, setLoading] = useState(true)
    const [editingId, setEditingId] = useState(null)
    const [editName, setEditName] = useState('')
    const [error, setError] = useState('')

    const { currentUser } = useAuth()

    // Load saved analyses
    useEffect(() => {
        async function loadAnalyses() {
            if (!currentUser) {
                setLoading(false)
                return
            }

            try {
                const data = await getUserAnalyses(currentUser.uid)
                setAnalyses(data)
            } catch (err) {
                console.error('Error loading analyses:', err)
                setError('Failed to load saved portfolios')
            } finally {
                setLoading(false)
            }
        }

        loadAnalyses()
    }, [currentUser])

    // Handle rename
    async function handleRename(id) {
        if (!editName.trim()) return

        try {
            await updateAnalysis(currentUser.uid, id, { name: editName })
            setAnalyses(analyses.map(a =>
                a.id === id ? { ...a, name: editName } : a
            ))
            setEditingId(null)
        } catch (err) {
            console.error('Error renaming:', err)
            setError('Failed to rename portfolio')
        }
    }

    // Handle delete
    async function handleDelete(id) {
        if (!window.confirm('Are you sure you want to delete this analysis?')) return

        try {
            await deleteAnalysis(currentUser.uid, id)
            setAnalyses(analyses.filter(a => a.id !== id))
        } catch (err) {
            console.error('Error deleting:', err)
            setError('Failed to delete portfolio')
        }
    }

    // Start editing
    function startEdit(analysis) {
        setEditingId(analysis.id)
        setEditName(analysis.name || '')
    }

    // Cancel editing
    function cancelEdit() {
        setEditingId(null)
        setEditName('')
    }

    if (!currentUser) {
        return (
            <div className="saved-portfolios">
                <div className="login-prompt">
                    <h3>🔐 Login Required</h3>
                    <p>Please login to view and manage your saved portfolio analyses.</p>
                </div>
            </div>
        )
    }

    if (loading) {
        return (
            <div className="saved-portfolios">
                <div className="loading">Loading your saved portfolios...</div>
            </div>
        )
    }

    return (
        <div className="saved-portfolios">
            <h2>📁 Saved Portfolios</h2>

            {error && <div className="error-message">{error}</div>}

            {analyses.length === 0 ? (
                <div className="empty-state">
                    <p>No saved portfolios yet.</p>
                    <p className="hint">Run an analysis and click "Save Analysis" to save it here.</p>
                </div>
            ) : (
                <div className="analyses-list">
                    {analyses.map(analysis => (
                        <div key={analysis.id} className="analysis-card">
                            <div className="analysis-header">
                                {editingId === analysis.id ? (
                                    <div className="edit-name">
                                        <input
                                            type="text"
                                            value={editName}
                                            onChange={(e) => setEditName(e.target.value)}
                                            onKeyDown={(e) => e.key === 'Enter' && handleRename(analysis.id)}
                                            autoFocus
                                        />
                                        <button onClick={() => handleRename(analysis.id)} className="save-btn">✓</button>
                                        <button onClick={cancelEdit} className="cancel-btn">✕</button>
                                    </div>
                                ) : (
                                    <h3 onClick={() => startEdit(analysis)}>
                                        {analysis.name || 'Unnamed Analysis'}
                                        <span className="edit-hint">✏️</span>
                                    </h3>
                                )}
                                <div className="analysis-meta">
                                    <span className="risk-badge" style={{
                                        background: getRiskColor(analysis.risk_score)
                                    }}>
                                        Risk: {analysis.risk_score?.toFixed(1) || 'N/A'}
                                    </span>
                                    <span className="date">
                                        {formatDate(analysis.savedAt)}
                                    </span>
                                </div>
                            </div>

                            <div className="analysis-preview">
                                <p>
                                    <strong>Holdings:</strong> {analysis.holdings?.length || 0} stocks
                                </p>
                                <p>
                                    <strong>Value:</strong> ${(analysis.total_value || 0).toLocaleString()}
                                </p>
                            </div>

                            <div className="analysis-actions">
                                <button
                                    className="load-btn"
                                    onClick={() => onLoadAnalysis(analysis)}
                                >
                                    View Analysis
                                </button>
                                <button
                                    className="delete-btn"
                                    onClick={() => handleDelete(analysis.id)}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

// Helper function to get risk color
function getRiskColor(score) {
    if (!score) return '#888'
    if (score <= 3) return '#4ecdc4'
    if (score <= 5) return '#f9ca24'
    if (score <= 7) return '#ff9f43'
    return '#ff6b6b'
}

// Helper function to format date
function formatDate(timestamp) {
    if (!timestamp) return 'Unknown date'
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    })
}

export default SavedPortfolios
