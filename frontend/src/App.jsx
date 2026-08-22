import { BrowserRouter, Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import Auth from './pages/Auth'
import Chat from './pages/Chat'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import en from './locales/en'
import ru from './locales/ru'
import './App.css'

const locales = { en, ru }

function Layout({ lang, setLang }) {
  const navigate = useNavigate()
  const t = useMemo(() => locales[lang] || en, [lang])

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/auth')
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-top">
          <h2 className="logo">Fina</h2>
          <nav>
            <NavLink to="/chat">{t.nav_chat}</NavLink>
            <NavLink to="/profile">{t.nav_profile}</NavLink>
            <NavLink to="/settings">{t.nav_settings}</NavLink>
          </nav>
        </div>
        <div className="sidebar-bottom">
          <select value={lang} onChange={e => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="ru">Русский</option>
          </select>
          <button className="btn-logout" onClick={logout}>{t.logout}</button>
        </div>
      </aside>
      <main className="main-content">
        <Routes>
          <Route path="/chat" element={<Chat lang={lang} t={t} />} />
          <Route path="/profile" element={<Profile t={t} />} />
          <Route path="/settings" element={<Settings t={t} />} />
          <Route path="*" element={<Navigate to="/chat" />} />
        </Routes>
      </main>
    </div>
  )
}

function RequireAuth({ children }) {
  return localStorage.getItem('token') ? children : <Navigate to="/auth" />
}

export default function App() {
  const [lang, setLang] = useState('en')

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/*" element={
          <RequireAuth>
            <Layout lang={lang} setLang={setLang} />
          </RequireAuth>
        } />
      </Routes>
    </BrowserRouter>
  )
}
