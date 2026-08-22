const BASE = ''

const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token')}`
})

export const api = {
  register: (username, email, password) =>
    fetch(`${BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    }),

  login: (username, password) =>
    fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    }),

  getProfile: () =>
    fetch(`${BASE}/users/profile`, { headers: authHeaders() }),

  updateProfile: (data) =>
    fetch(`${BASE}/users/profile`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data)
    }),

  updateAccount: (data) =>
    fetch(`${BASE}/users/account`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data)
    }),

  getAvatar: () => `${BASE}/users/avatar`,

  uploadAvatar: (file) => {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${BASE}/users/avatar`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: form
    })
  },

  getHistory: () =>
    fetch(`${BASE}/chat/history`, { headers: authHeaders() }),

  sendMessage: (message, lang) =>
    fetch(`${BASE}/chat/send`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ message, lang })
    }),
}
