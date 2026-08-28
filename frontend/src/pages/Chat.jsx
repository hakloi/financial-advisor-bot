import { useState, useEffect, useRef } from 'react'
import { api, readResponse } from '../api'

export default function Chat({ lang, t }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [thinking, setThinking] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    api.getHistory().then(readResponse).then(data => {
      if (Array.isArray(data)) setMessages(data)
    }).catch(error => setMessages([{ role: 'assistant', content: error.message, created_at: new Date().toISOString() }]))
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

  const copyMessage = async (content) => {
    await navigator.clipboard.writeText(content)
  }

  const removeMessage = async (messageId) => {
    try {
      const res = await api.deleteMessage(messageId)
      if (res.ok) setMessages(prev => prev.filter(message => message.id !== messageId))
      else throw new Error((await res.json().catch(() => ({}))).detail || 'Could not delete message')
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: error.message, created_at: new Date().toISOString() }])
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input, created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setThinking(true)

    let res
    try {
      res = await api.sendMessage(input, lang)
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: error.message, created_at: new Date().toISOString() }])
      setLoading(false)
      setThinking(false)
      return
    }
    const userMessageId = Number(res.headers.get('X-User-Message-ID'))
    if (userMessageId > 0) {
      setMessages(prev => prev.map((message, index) =>
        index === prev.length - 1 ? { ...message, id: userMessageId } : message
      ))
    }
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.detail || 'The assistant is temporarily unavailable.',
        created_at: new Date().toISOString(),
      }])
      setLoading(false)
      setThinking(false)
      return
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    let botContent = ''
    let firstChunk = true
    const botTs = new Date().toISOString()
    const assistantMessageId = Number(res.headers.get('X-Assistant-Message-ID'))

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        botContent += decoder.decode(value)

        if (firstChunk) {
          firstChunk = false
          setThinking(false)
          setMessages(prev => [...prev, { id: assistantMessageId, role: 'assistant', content: botContent, created_at: botTs }])
        } else {
          setMessages(prev => prev.map((m, i) =>
            i === prev.length - 1 ? { ...m, content: botContent } : m
          ))
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: error.message, created_at: new Date().toISOString() }])
    }

    setLoading(false)
    setThinking(false)
  }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => {
          const msgDate = msg.created_at ? formatDate(msg.created_at) : null
          const previousDate = i > 0 && messages[i - 1].created_at
            ? formatDate(messages[i - 1].created_at)
            : null
          const showDate = msgDate && msgDate !== previousDate

          return (
            <div key={msg.id || `${msg.role}-${i}`}>
              {showDate && <div className="date-separator">{msgDate}</div>}
              <div className={`message-row ${msg.role}`}>
                <div className={`message ${msg.role}`}>
                  <div className="content">{msg.content}</div>
                  {msg.id && (
                    <div className="message-actions">
                      <button type="button" onClick={() => copyMessage(msg.content)}>Copy</button>
                      <button type="button" onClick={() => removeMessage(msg.id)}>Delete</button>
                    </div>
                  )}
                  {msg.created_at && <div className="time">{formatTime(msg.created_at)}</div>}
                </div>
              </div>
            </div>
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
