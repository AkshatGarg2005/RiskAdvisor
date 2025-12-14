// Auth Modal - Login/Signup modal component
import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import './AuthModal.css'

function AuthModal({ isOpen, onClose }) {
    const [isLogin, setIsLogin] = useState(true)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const { login, signup } = useAuth()

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')

        // Validation
        if (!email || !password) {
            return setError('Please fill in all fields')
        }

        if (!isLogin && password !== confirmPassword) {
            return setError('Passwords do not match')
        }

        if (password.length < 6) {
            return setError('Password must be at least 6 characters')
        }

        try {
            setLoading(true)
            if (isLogin) {
                await login(email, password)
            } else {
                await signup(email, password)
            }
            onClose()
        } catch (err) {
            console.error('Auth error:', err)
            if (err.code === 'auth/user-not-found') {
                setError('No account found with this email')
            } else if (err.code === 'auth/wrong-password') {
                setError('Incorrect password')
            } else if (err.code === 'auth/email-already-in-use') {
                setError('Email already in use')
            } else if (err.code === 'auth/invalid-email') {
                setError('Invalid email address')
            } else {
                setError('Authentication failed. Please try again.')
            }
        } finally {
            setLoading(false)
        }
    }

    function toggleMode() {
        setIsLogin(!isLogin)
        setError('')
        setPassword('')
        setConfirmPassword('')
    }

    if (!isOpen) return null

    return (
        <div className="auth-modal-overlay" onClick={onClose}>
            <div className="auth-modal" onClick={e => e.stopPropagation()}>
                <button className="close-btn" onClick={onClose}>&times;</button>

                <h2>{isLogin ? '🔐 Login' : '📝 Sign Up'}</h2>

                {error && <div className="auth-error">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="your@email.com"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            disabled={loading}
                        />
                    </div>

                    {!isLogin && (
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="••••••••"
                                disabled={loading}
                            />
                        </div>
                    )}

                    <button type="submit" className="auth-submit-btn" disabled={loading}>
                        {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
                    </button>
                </form>

                <p className="toggle-mode">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button type="button" onClick={toggleMode} disabled={loading}>
                        {isLogin ? 'Sign Up' : 'Login'}
                    </button>
                </p>
            </div>
        </div>
    )
}

export default AuthModal
