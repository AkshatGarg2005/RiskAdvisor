import { useState } from 'react'
import './App.css'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import RiskDashboard from './components/RiskDashboard'
import PortfolioForm from './components/PortfolioForm'
import AuthModal from './components/AuthModal'
import SavedPortfolios from './components/SavedPortfolios'
import ChatWindow from './components/ChatWindow'
import { saveAnalysis } from './services/portfolioService'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function AppContent() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('form') // 'form', 'csv', 'test', 'saved'
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null) // 'saving', 'saved', 'error'
  const [showChat, setShowChat] = useState(false)

  const { currentUser, logout } = useAuth()

  const analyzePortfolio = async (portfolio) => {
    setLoading(true)
    setError(null)
    setSaveStatus(null)
    try {
      const response = await fetch(`${API_BASE}/analyze-portfolio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(portfolio)
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`)
      }
      const data = await response.json()
      setAnalysisResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadTestPortfolio = async (type) => {
    setLoading(true)
    setError(null)
    setSaveStatus(null)
    try {
      const response = await fetch(`${API_BASE}/test-portfolio?type=${type}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`)
      }
      const data = await response.json()
      setAnalysisResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const uploadCSV = async (file, userProfile) => {
    setLoading(true)
    setError(null)
    setSaveStatus(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch(
        `${API_BASE}/upload-portfolio-csv?user_profile=${userProfile}`,
        { method: 'POST', body: formData }
      )
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`)
      }
      const data = await response.json()
      setAnalysisResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const downloadTemplate = async () => {
    window.open(`${API_BASE}/csv-template`, '_blank')
  }

  const handleSaveAnalysis = async () => {
    if (!currentUser || !analysisResult) return

    try {
      setSaveStatus('saving')
      await saveAnalysis(currentUser.uid, analysisResult)
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus(null), 3000)
    } catch (err) {
      console.error('Save error:', err)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus(null), 3000)
    }
  }

  const handleLoadAnalysis = (analysis) => {
    setAnalysisResult(analysis)
    setActiveTab('form') // Switch to form tab to show the analysis
    setSaveStatus(null)
  }

  const handleLogout = async () => {
    try {
      await logout()
      setAnalysisResult(null)
      setSaveStatus(null)
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🛡️ RiskAdvisor</h1>
            <p>AI-Powered Investment Risk Analysis</p>
          </div>
          <div className="auth-section">
            {currentUser ? (
              <div className="user-info">
                <span className="user-email">{currentUser.email}</span>
                <button onClick={handleLogout} className="auth-btn logout">
                  Logout
                </button>
              </div>
            ) : (
              <button onClick={() => setShowAuthModal(true)} className="auth-btn login">
                🔐 Login
              </button>
            )}
          </div>
        </div>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === 'form' ? 'active' : ''}
          onClick={() => setActiveTab('form')}
        >
          Manual Entry
        </button>
        <button
          className={activeTab === 'csv' ? 'active' : ''}
          onClick={() => setActiveTab('csv')}
        >
          CSV Upload
        </button>
        {currentUser && (
          <button
            className={activeTab === 'saved' ? 'active' : ''}
            onClick={() => setActiveTab('saved')}
          >
            📁 Saved
          </button>
        )}
      </nav>

      <main className="main-content">
        {error && <div className="error-banner">{error}</div>}

        {activeTab === 'saved' ? (
          <SavedPortfolios onLoadAnalysis={handleLoadAnalysis} />
        ) : (
          <>
            <div className="input-section">
              {activeTab === 'form' && (
                <PortfolioForm onSubmit={analyzePortfolio} loading={loading} />
              )}

              {activeTab === 'csv' && (
                <div className="csv-upload">
                  <h2>Upload Portfolio CSV</h2>
                  <button onClick={downloadTemplate} className="secondary-btn">
                    📥 Download Template
                  </button>
                  <form onSubmit={(e) => {
                    e.preventDefault()
                    const file = e.target.csvFile.files[0]
                    const profile = e.target.userProfile.value
                    if (file) uploadCSV(file, profile)
                  }}>
                    <div className="form-group">
                      <label>User Profile:</label>
                      <select name="userProfile">
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="senior">Senior</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>CSV File:</label>
                      <input type="file" name="csvFile" accept=".csv" required />
                    </div>
                    <button type="submit" disabled={loading} className="primary-btn">
                      {loading ? 'Analyzing...' : 'Upload & Analyze'}
                    </button>
                  </form>
                </div>
              )}

            </div>

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Analyzing portfolio with AI agents...</p>
              </div>
            )}

            {analysisResult && !loading && (
              <div className="analysis-result">
                {currentUser && (
                  <div className="save-section">
                    <button
                      onClick={handleSaveAnalysis}
                      disabled={saveStatus === 'saving'}
                      className={`save-btn ${saveStatus || ''}`}
                    >
                      {saveStatus === 'saving' && '⏳ Saving...'}
                      {saveStatus === 'saved' && '✅ Saved!'}
                      {saveStatus === 'error' && '❌ Error'}
                      {!saveStatus && '💾 Save Analysis'}
                    </button>
                  </div>
                )}
                <RiskDashboard data={analysisResult} />
              </div>
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Built for 10-hour hackathon | Google ADK + FastAPI + React + Firebase</p>
      </footer>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      <ChatWindow
        portfolioData={analysisResult}
        isOpen={showChat}
        onClose={() => setShowChat(false)}
      />

      {/* Floating Chat Button */}
      {analysisResult && !showChat && (
        <button
          className="floating-chat-btn"
          onClick={() => setShowChat(true)}
          title="Ask about your portfolio"
        >
          💬
        </button>
      )}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
