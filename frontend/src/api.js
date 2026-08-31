const BASE = ''

const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token')}`
})

export const readResponse = async (response) => {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || 'Request failed')
  return data
}

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

  confirmEmail: (token) =>
    fetch(`${BASE}/auth/confirm?token=${encodeURIComponent(token)}`),

  getProfile: () =>
    fetch(`${BASE}/users/profile`, { headers: authHeaders() }),

  getRecommendations: () =>
    fetch(`${BASE}/users/recommendations`, { headers: authHeaders() }),

  getTransactions: (year, month) =>
    fetch(`${BASE}/users/transactions?year=${year}&month=${month}`, { headers: authHeaders() }),

  addTransaction: (data) =>
    fetch(`${BASE}/users/transactions`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data)
    }),

  updateTransaction: (transactionId, data) =>
    fetch(`${BASE}/users/transactions/${transactionId}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data)
    }),

  deleteTransaction: (transactionId) =>
    fetch(`${BASE}/users/transactions/${transactionId}`, {
      method: 'DELETE',
      headers: authHeaders(),
    }),

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

  deleteAvatar: () =>
    fetch(`${BASE}/users/avatar`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
    }),

  getHistory: () =>
    fetch(`${BASE}/chat/history`, { headers: authHeaders() }),

  deleteMessage: (messageId) =>
    fetch(`${BASE}/chat/messages/${messageId}`, {
      method: 'DELETE',
      headers: authHeaders(),
    }),

  sendMessage: (message, lang) =>
    fetch(`${BASE}/chat/send`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ message, lang })
    }),
}
