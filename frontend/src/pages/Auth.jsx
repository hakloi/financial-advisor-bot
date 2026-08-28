import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, readResponse } from '../api'

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
      const data = await readResponse(res)
      setError(data.detail)
      setTab('login')
    }).catch((error) => setError(error.message || 'Could not confirm email'))
  }, [])

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const data = await readResponse(await api.login(form.username, form.password))
      localStorage.setItem('token', data.access_token)
      navigate('/chat')
    } catch (error) {
      setError(error.message)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await readResponse(await api.register(form.username, form.email, form.password))
      setTab('login')
      setError('Account created! Check your email and confirm it before logging in.')
    } catch (error) {
      setError(error.message)
    }
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
