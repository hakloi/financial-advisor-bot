import { useRef, useState, useEffect } from 'react'
import { api } from '../api'
import defaultAvatar from '../assets/anon-icon.jpg'

export default function Profile({ t }) {
  const [profile, setProfile] = useState(null)
  const [saved, setSaved] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState(null)
  const avatarInput = useRef(null)

  const loadAvatar = () => {
    fetch('/users/avatar', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    }).then(r => {
      if (r.ok) return r.blob()
    }).then(blob => {
      if (blob) setAvatarUrl(URL.createObjectURL(blob))
    })
  }

  useEffect(() => {
    api.getProfile().then(r => r.json()).then(setProfile)
    loadAvatar()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    await api.updateProfile({
      age: profile.age,
      current_savings: profile.current_savings,
      currency: profile.currency,
      risk_level: profile.risk_level,
      investment_horizon: profile.investment_horizon,
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleAvatar = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    await api.uploadAvatar(file)
    loadAvatar()
  }

  const handleDeleteAvatar = async () => {
    const res = await api.deleteAvatar()
    if (res.ok) setAvatarUrl(null)
  }

  const set = (field) => (e) => setProfile({ ...profile, [field]: e.target.value })

  if (!profile) return <p style={{ padding: 32 }}>{t.loading}</p>

  return (
    <div className="page-container">
      <div className="page-inner">
        <h2>{t.profile_title}</h2>

        <div className="profile-heading">
          <p className="username">@{profile.username}</p>
          <p className="registration-date">{t.profile_registered}: {new Date(profile.created_at).toLocaleDateString()}</p>
        </div>

        <div className="avatar-section">
          <img src={avatarUrl || defaultAvatar} alt="avatar" className="avatar" />
          <div className="avatar-actions">
            <button type="button" className="avatar-button avatar-upload" onClick={() => avatarInput.current?.click()}>
              {t.profile_change_avatar}
            </button>
            <input ref={avatarInput} type="file" accept="image/*" onChange={handleAvatar} hidden />
            {avatarUrl && <button type="button" className="avatar-button avatar-delete" onClick={handleDeleteAvatar}>{t.profile_delete_avatar}</button>}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <label>{t.profile_age}
            <input type="number" min={1} max={110} value={profile.age ?? ''} onChange={set('age')} />
          </label>
          <label>{t.profile_savings}
            <input type="number" min={0} step="0.01" value={profile.current_savings ?? ''} onChange={set('current_savings')} />
          </label>
          <label>{t.profile_currency}
            <select value={profile.currency ?? 'RUB'} onChange={set('currency')}>
              <option>RUB</option>
              <option>USD</option>
            </select>
          </label>
          <label>{t.profile_risk}
            <select value={profile.risk_level ?? 'medium'} onChange={set('risk_level')}>
              <option value="low">{t.profile_risk_low}</option>
              <option value="medium">{t.profile_risk_medium}</option>
              <option value="high">{t.profile_risk_high}</option>
            </select>
          </label>
          <label>{t.profile_horizon}
            <select value={profile.investment_horizon ?? 'short'} onChange={set('investment_horizon')}>
              <option value="short">{t.profile_horizon_short}</option>
              <option value="medium">{t.profile_horizon_medium}</option>
              <option value="long">{t.profile_horizon_long}</option>
            </select>
          </label>
          <button type="submit">{t.profile_save}</button>
          {saved && <span className="success">{t.profile_saved}</span>}
        </form>
      </div>
    </div>
  )
}
