import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Settings({ t }) {
  const [form, setForm] = useState({ username: '', email: '', current_password: '', new_password: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    api.getProfile().then(r => r.json()).then(data => {
      setForm(f => ({ ...f, username: data.username, email: data.email }))
    })
  }, [])

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    const res = await api.updateAccount({
      username: form.username || undefined,
      email: form.email || undefined,
      current_password: form.current_password || undefined,
      new_password: form.new_password || undefined,
    })
    const data = await res.json()
    if (!res.ok) return setError(data.detail)
    setSuccess(t.settings_saved)
    setForm(f => ({ ...f, current_password: '', new_password: '' }))
  }

  return (
    <div className="page-container">
      <div className="page-inner">
        <h2>{t.settings_title}</h2>
        <form onSubmit={handleSubmit}>
          <label>{t.settings_username}
            <input value={form.username} onChange={set('username')} />
          </label>
          <label>{t.settings_email}
            <input type="email" value={form.email} onChange={set('email')} />
          </label>
          <label>{t.settings_current_password}
            <input type="password" value={form.current_password} onChange={set('current_password')} />
          </label>
          <label>{t.settings_new_password}
            <input type="password" value={form.new_password} onChange={set('new_password')} />
          </label>
          <button type="submit">{t.settings_save}</button>
          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}
        </form>
      </div>
    </div>
  )
}
