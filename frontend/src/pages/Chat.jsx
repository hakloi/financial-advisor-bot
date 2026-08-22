import { useState, useEffect, useRef } from 'react'
import { api } from '../api'

export default function Chat({ lang, t }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [thinking, setThinking] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    api.getHistory().then(r => r.json()).then(data => {
      if (Array.isArray(data)) setMessages(data)
    })
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  const formatDate = (ts) => {
    const d = new Date(ts)
    const today = new Date()
    const diff = Math.floor((today - d) / 86400000)
    if (diff === 0) return t.chat_today
    if (diff === 1) return t.chat_yesterday
    return d.toLocaleDateString()
  }

  const formatTime = (ts) => new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input, created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setThinking(true)

    const res = await api.sendMessage(input, lang)
    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    let botContent = ''
    let firstChunk = true
    const botTs = new Date().toISOString()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      botContent += decoder.decode(value)

      if (firstChunk) {
        firstChunk = false
        setThinking(false)
        setMessages(prev => [...prev, { role: 'assistant', content: botContent, created_at: botTs }])
      } else {
        setMessages(prev => prev.map((m, i) =>
          i === prev.length - 1 ? { ...m, content: botContent } : m
        ))
      }
    }

    setLoading(false)
    setThinking(false)
  }

  let lastDate = null

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => {
          const msgDate = msg.created_at ? formatDate(msg.created_at) : null
          const showDate = msgDate && msgDate !== lastDate
          if (showDate) lastDate = msgDate

          return (
            <>
              {showDate && <div className="date-separator">{msgDate}</div>}
              <div key={i} className={`message-row ${msg.role}`}>
                <div className={`message ${msg.role}`}>
                  <div className="content">{msg.content}</div>
                  {msg.created_at && <div className="time">{formatTime(msg.created_at)}</div>}
                </div>
              </div>
            </>
          )
        })}

        {thinking && (
          <div className="message-row assistant">
            <div className="message assistant">
              <div className="content thinking"><span /><span /><span /></div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form className="chat-input" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={t.chat_placeholder}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>{t.chat_send}</button>
      </form>
    </div>
  )
}
