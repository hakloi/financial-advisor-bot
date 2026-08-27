import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function Auth() {
  const [tab, setTab] = useState('login')
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const confirmationRequested = useRef(false)

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('token')
    if (!token || confirmationRequested.current) return
    confirmationRequested.current = true

    api.confirmEmail(token).then(async (res) => {
      const data = await res.json()
      setError(res.ok ? data.detail : data.detail || 'Confirmation link is invalid or expired')
      if (res.ok) setTab('login')
    }).catch(() => setError('Could not confirm email'))
  }, [])

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    const res = await api.login(form.username, form.password)
    const data = await res.json()
    if (!res.ok) return setError(data.detail)
    localStorage.setItem('token', data.access_token)
    navigate('/chat')
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    const res = await api.register(form.username, form.email, form.password)
    const data = await res.json()
    if (!res.ok) return setError(data.detail)
    setTab('login')
    setError('Account created! Check your email and confirm it before logging in.')
  }

  return (
    <div className="auth-page">
    <div className="auth-container">
      <h1>Fina</h1>
      <div className="tabs">
        <button className={tab === 'login' ? 'active' : ''} onClick={() => setTab('login')}>Login</button>
        <button className={tab === 'register' ? 'active' : ''} onClick={() => setTab('register')}>Register</button>
      </div>

      {tab === 'login' ? (
        <form onSubmit={handleLogin}>
          <input placeholder="Username" value={form.username} onChange={set('username')} required />
          <input placeholder="Password" type="password" value={form.password} onChange={set('password')} required />
          <button type="submit">Login</button>
        </form>
      ) : (
        <form onSubmit={handleRegister}>
          <input placeholder="Username" value={form.username} onChange={set('username')} required />
          <input placeholder="Email" type="email" value={form.email} onChange={set('email')} required />
          <input placeholder="Password" type="password" value={form.password} onChange={set('password')} required />
          <button type="submit">Register</button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
    </div>
    </div>
  )
}
