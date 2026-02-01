import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './DoctorChat.css'
import './AyushChat.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  references?: Array<{
    source_text: string
    chapter?: string
    relevance_score?: number
  }>
  databases_consulted?: string[]
}

interface ChatResponse {
  success: boolean
  query_id: string
  mode: string
  response: string
  references: Array<{
    source_text: string
    chapter?: string
    relevance_score?: number
  }>
  databases_consulted: string[]
}

// Parse inline formatting (bold, italic, code)
const parseInlineFormatting = (text: string): React.ReactNode => {
  const parts: React.ReactNode[] = []
  let remaining = text
  let key = 0

  while (remaining.length > 0) {
    const boldMatch = remaining.match(/^(.*?)\*\*(.+?)\*\*(.*)$/s)
    if (boldMatch) {
      if (boldMatch[1]) parts.push(<span key={key++}>{parseInlineFormatting(boldMatch[1])}</span>)
      parts.push(<strong key={key++}>{parseInlineFormatting(boldMatch[2])}</strong>)
      remaining = boldMatch[3]
      continue
    }

    const italicMatch = remaining.match(/^(.*?)(?:\*(.+?)\*|_(.+?)_)(.*)$/s)
    if (italicMatch) {
      if (italicMatch[1]) parts.push(<span key={key++}>{italicMatch[1]}</span>)
      parts.push(<em key={key++}>{italicMatch[2] || italicMatch[3]}</em>)
      remaining = italicMatch[4]
      continue
    }

    const codeMatch = remaining.match(/^(.*?)`(.+?)`(.*)$/s)
    if (codeMatch) {
      if (codeMatch[1]) parts.push(<span key={key++}>{codeMatch[1]}</span>)
      parts.push(<code key={key++}>{codeMatch[2]}</code>)
      remaining = codeMatch[3]
      continue
    }

    parts.push(<span key={key++}>{remaining}</span>)
    break
  }

  return parts.length === 1 ? parts[0] : <>{parts}</>
}

// Parse markdown table
const parseTable = (lines: string[], startIndex: number): { element: React.ReactNode; endIndex: number } => {
  const tableLines: string[] = []
  let i = startIndex

  while (i < lines.length && lines[i].includes('|')) {
    tableLines.push(lines[i])
    i++
  }

  if (tableLines.length < 2) {
    return { element: null, endIndex: startIndex }
  }

  const headerCells = tableLines[0].split('|').filter(cell => cell.trim() !== '')
  const dataStartIndex = tableLines[1].includes('-') ? 2 : 1
  const dataRows = tableLines.slice(dataStartIndex).map(line => 
    line.split('|').filter(cell => cell.trim() !== '')
  )

  const element = (
    <div className="table-wrapper" key={`table-${startIndex}`}>
      <table>
        <thead>
          <tr>
            {headerCells.map((cell, j) => (
              <th key={j}>{parseInlineFormatting(cell.trim())}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, j) => (
            <tr key={j}>
              {row.map((cell, k) => (
                <td key={k}>{parseInlineFormatting(cell.trim())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  return { element, endIndex: i - 1 }
}

// Section icons for AYUSH framework
const sectionIcons: Record<string, string> = {
  'panchamahabhuta': '🌍',
  'five elements': '🌍',
  'tridosha': '☯️',
  'dosha': '☯️',
  'vata': '💨',
  'pitta': '🔥',
  'kapha': '💧',
  'saptadhatu': '🧬',
  'dhatu': '🧬',
  'tissue': '🧬',
  'agni': '🔥',
  'digestive': '🔥',
  'ama': '⚠️',
  'mala': '♻️',
  'waste': '♻️',
  'elimination': '♻️',
  'swasthya': '✨',
  'wellness': '✨',
  'health': '✨',
  'ahara': '🍽️',
  'diet': '🍽️',
  'food': '🍽️',
  'vihara': '🏃',
  'lifestyle': '🏃',
  'aushadhi': '🌿',
  'herb': '🌿',
  'medicine': '🌿',
  'formulation': '🌿',
  'yoga': '🧘',
  'pranayama': '🧘',
  'intervention': '💊',
  'recommendation': '📋',
  'treatment': '💊',
}

const getSectionIcon = (text: string): string => {
  const lowerText = text.toLowerCase()
  for (const [keyword, icon] of Object.entries(sectionIcons)) {
    if (lowerText.includes(keyword)) {
      return icon
    }
  }
  return '📌'
}

function AyushChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/chat/ayush', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content })
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data: ChatResponse = await response.json()

      const assistantMessage: Message = {
        id: data.query_id,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        references: data.references,
        databases_consulted: data.databases_consulted
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setIsLoading(false)
    }
  }

  const formatMessage = (content: string) => {
    const lines = content.split('\n')
    const elements: React.ReactNode[] = []
    let i = 0
    let listItems: React.ReactNode[] = []
    let listType: 'ul' | 'ol' | null = null

    const flushList = () => {
      if (listItems.length > 0) {
        if (listType === 'ol') {
          elements.push(<ol key={`list-${elements.length}`}>{listItems}</ol>)
        } else {
          elements.push(<ul key={`list-${elements.length}`}>{listItems}</ul>)
        }
        listItems = []
        listType = null
      }
    }

    while (i < lines.length) {
      const line = lines[i]

      // Check for table
      if (line.includes('|') && line.trim().startsWith('|')) {
        flushList()
        const { element, endIndex } = parseTable(lines, i)
        if (element) {
          elements.push(element)
          i = endIndex + 1
          continue
        }
      }

      // Section headers with icons (h2, h3, h4)
      if (line.startsWith('#### ')) {
        flushList()
        const headerText = line.slice(5)
        const icon = getSectionIcon(headerText)
        elements.push(
          <h5 key={i} className="ayush-section-header h5">
            <span className="section-icon">{icon}</span>
            {parseInlineFormatting(headerText)}
          </h5>
        )
        i++
        continue
      }
      if (line.startsWith('### ')) {
        flushList()
        const headerText = line.slice(4)
        const icon = getSectionIcon(headerText)
        elements.push(
          <h4 key={i} className="ayush-section-header h4">
            <span className="section-icon">{icon}</span>
            {parseInlineFormatting(headerText)}
          </h4>
        )
        i++
        continue
      }
      if (line.startsWith('## ')) {
        flushList()
        const headerText = line.slice(3)
        const icon = getSectionIcon(headerText)
        elements.push(
          <h3 key={i} className="ayush-section-header h3">
            <span className="section-icon">{icon}</span>
            {parseInlineFormatting(headerText)}
          </h3>
        )
        i++
        continue
      }
      if (line.startsWith('# ')) {
        flushList()
        const headerText = line.slice(2)
        const icon = getSectionIcon(headerText)
        elements.push(
          <h2 key={i} className="ayush-section-header h2">
            <span className="section-icon">{icon}</span>
            {parseInlineFormatting(headerText)}
          </h2>
        )
        i++
        continue
      }

      // Framework keywords highlighting
      if (line.startsWith('- ') || line.startsWith('• ') || line.startsWith('* ')) {
        if (listType === 'ol') flushList()
        listType = 'ul'
        listItems.push(<li key={i}>{parseInlineFormatting(line.slice(2))}</li>)
        i++
        continue
      }

      if (/^\d+\.\s/.test(line)) {
        if (listType === 'ul') flushList()
        listType = 'ol'
        listItems.push(<li key={i}>{parseInlineFormatting(line.replace(/^\d+\.\s/, ''))}</li>)
        i++
        continue
      }

      if (line.trim() === '') {
        flushList()
        elements.push(<br key={i} />)
        i++
        continue
      }

      // Highlight framework terms in regular paragraphs
      flushList()
      elements.push(<p key={i}>{parseInlineFormatting(line)}</p>)
      i++
    }

    flushList()
    return elements
  }

  return (
    <div className="doctor-chat ayush-chat">
      <header className="chat-header">
        <Link to="/" className="back-button">← Back</Link>
        <div className="header-content">
          <h1>🏛️ AYUSH Chat</h1>
          <p>Ministry of AYUSH aligned comprehensive Ayurvedic analysis</p>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message ayush-welcome">
              <h2>Welcome to AYUSH Chat</h2>
              <p>Get comprehensive analysis through the complete Ayurvedic framework.</p>
              
              <div className="framework-overview">
                <div className="framework-item">
                  <span className="fw-icon">🌍</span>
                  <div>
                    <strong>Panchamahabhuta</strong>
                    <span>5 Elements: Akasha, Vayu, Agni, Jala, Prithvi</span>
                  </div>
                </div>
                <div className="framework-item">
                  <span className="fw-icon">☯️</span>
                  <div>
                    <strong>Tridosha</strong>
                    <span>Vata, Pitta, Kapha balance</span>
                  </div>
                </div>
                <div className="framework-item">
                  <span className="fw-icon">🧬</span>
                  <div>
                    <strong>Saptadhatu</strong>
                    <span>7 Tissues health assessment</span>
                  </div>
                </div>
                <div className="framework-item">
                  <span className="fw-icon">🔥</span>
                  <div>
                    <strong>Agni & Ama</strong>
                    <span>Digestive fire & toxin analysis</span>
                  </div>
                </div>
                <div className="framework-item">
                  <span className="fw-icon">♻️</span>
                  <div>
                    <strong>Mala</strong>
                    <span>Waste elimination status</span>
                  </div>
                </div>
                <div className="framework-item">
                  <span className="fw-icon">💊</span>
                  <div>
                    <strong>Interventions</strong>
                    <span>Ahara, Vihara, Aushadhi, Yoga</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {messages.map(message => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-content">
                {message.role === 'user' ? (
                  <p>{message.content}</p>
                ) : (
                  <div className="assistant-content ayush-response">
                    {formatMessage(message.content)}
                    
                    {message.databases_consulted && message.databases_consulted.length > 0 && (
                      <div className="metadata">
                        <span className="databases">
                          📚 Classical Sources: {message.databases_consulted.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <span className="timestamp">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator ayush-loading">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p className="loading-text">Analyzing through Ayurvedic frameworks...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>⚠️ {error}</p>
              <p>Make sure the backend server is running on port 8000.</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form className="input-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask for comprehensive Ayurvedic analysis..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AyushChat
