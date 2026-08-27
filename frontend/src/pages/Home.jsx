import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Home({ t }) {
  const [username, setUsername] = useState('')

  useEffect(() => {
    api.getProfile().then(response => response.json()).then(data => {
      if (data.username) setUsername(data.username)
    })
  }, [])

  return (
    <div className="home-page">
      <div className="home-content">
        <p className="home-kicker">Fina</p>
        <h1>{t.home_welcome}, {username || t.home_user}!</h1>
        <p className="home-message">{t.home_message}</p>
      </div>
    </div>
  )
}