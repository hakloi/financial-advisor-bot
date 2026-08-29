import { BrowserRouter, Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom' // 
import { useState, useMemo, useEffect, useRef } from 'react'
import Auth from './pages/Auth'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import en from './locales/en'
import ru from './locales/ru'
import './App.css'

// Define the available locales for the application
const locales = { en, ru }

// Main layout component for the application
function Layout({ lang, setLang }) {
  const navigate = useNavigate()
  const t = useMemo(() => locales[lang] || en, [lang])
  const [sidebarWidth, setSidebarWidth] = useState(240)
  const isNarrow = sidebarWidth < 180
  const isResizing = useRef(false)

  useEffect(() => {
    const resize = (event) => {
      if (!isResizing.current) return
      setSidebarWidth(Math.min(360, Math.max(50, event.clientX)))
    }
    const stopResize = () => { isResizing.current = false }
    window.addEventListener('pointermove', resize)
    window.addEventListener('pointerup', stopResize)
    return () => {
      window.removeEventListener('pointermove', resize)
      window.removeEventListener('pointerup', stopResize)
    }
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/auth')
  }

  return (
    <div className={`app ${isNarrow ? 'sidebar-collapsed' : ''}`}>
      <aside className="sidebar" style={{ width: `${sidebarWidth}px` }}>
        <button
          className="sidebar-toggle"
          type="button"
          onClick={() => setSidebarWidth(isNarrow ? 240 : 50)}
          aria-label={isNarrow ? 'Expand sidebar' : 'Collapse sidebar'}
          title={isNarrow ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isNarrow ? '>' : '<'}
        </button>
        <div
          className="sidebar-resize-handle"
          onPointerDown={(event) => {
            isResizing.current = true
            event.currentTarget.setPointerCapture(event.pointerId)
          }}
          aria-label="Resize sidebar"
        />
        <div className="sidebar-top">
          <h2 className="logo">Fina</h2>
          <nav>
            <NavLink to="/home">{t.nav_home}</NavLink>
            <NavLink to="/chat">{t.nav_chat}</NavLink>
            <NavLink to="/profile">{t.nav_profile}</NavLink>
            <NavLink to="/settings">{t.nav_settings}</NavLink>
          </nav>
        </div>
        <div className="sidebar-bottom">
          <select value={lang} onChange={e => setLang(e.target.value)} aria-label="Language">
            <option value="en">English</option>
            <option value="ru">Русский</option>
          </select>
          {!isNarrow && <button className="btn-logout" onClick={logout}>{t.logout}</button>}
        </div>
      </aside>
      <main className="main-content">
        <Routes>
          <Route path="/home" element={<Home t={t} />} />
          <Route path="/chat" element={<Chat lang={lang} t={t} />} />
          <Route path="/profile" element={<Profile t={t} />} />
          <Route path="/settings" element={<Settings t={t} />} />
          <Route path="*" element={<Navigate to="/home" />} />
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
        <Route path="/auth/*" element={<Auth />} />
        <Route path="/confirm-email" element={<Auth />} />
        <Route path="/*" element={
          <RequireAuth>
            <Layout lang={lang} setLang={setLang} />
          </RequireAuth>
        } />
      </Routes>
    </BrowserRouter>
  )
}
