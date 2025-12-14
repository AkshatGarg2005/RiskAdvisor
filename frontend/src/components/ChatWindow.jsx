// ChatWindow - Floating chat interface for portfolio Q&A
import { useState, useRef, useEffect } from 'react'
import './ChatWindow.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ChatWindow({ portfolioData, isOpen, onClose }) {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "Hi! I'm your portfolio assistant. Ask me anything about your current portfolio analysis - like risk levels, specific holdings, or recommendations."
        }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)

    // Scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim() || loading) return

        const userMessage = input.trim()
        setInput('')

        // Add user message to chat
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setLoading(true)

        try {
            // Get last 15 messages for conversation history (excluding the new user message)
            const recentHistory = messages.slice(-15).map(msg => ({
                role: msg.role,
                content: msg.content
            }))

            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    portfolio_context: portfolioData || {},
                    chat_history: recentHistory
                })
            })

            const data = await response.json()

            if (data.success) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.answer
                }])
            } else {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.answer || "Sorry, I couldn't process your question. Please try again."
                }])
            }
        } catch (error) {
            console.error('Chat error:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Sorry, there was an error connecting to the server. Please try again."
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    if (!isOpen) return null

    return (
        <div className="chat-overlay" onClick={onClose}>
            <div className="chat-window" onClick={e => e.stopPropagation()}>
                <div className="chat-header">
                    <div className="chat-title">
                        <span className="chat-icon">💬</span>
                        Portfolio Assistant
                    </div>
                    <button className="close-btn" onClick={onClose}>&times;</button>
                </div>

                <div className="chat-messages">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.role}`}>
                            <div className="message-content">
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="message assistant">
                            <div className="message-content typing">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    {!portfolioData && (
                        <div className="no-portfolio-warning">
                            ⚠️ Run a portfolio analysis first for personalized answers
                        </div>
                    )}
                    <div className="chat-input-container">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask about your portfolio..."
                            disabled={loading}
                            rows={1}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!input.trim() || loading}
                            className="send-btn"
                        >
                            {loading ? '⏳' : '➤'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ChatWindow
