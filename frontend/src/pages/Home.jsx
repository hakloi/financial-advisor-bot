import { useEffect, useMemo, useState } from 'react'
import { api, readResponse } from '../api'

const CATEGORY_OPTIONS = {
  income: ['salary', 'freelance', 'business', 'gift', 'interest', 'other'],
  expense: ['housing', 'food', 'transport', 'shopping', 'health', 'entertainment', 'utilities', 'travel', 'other'],
}

export default function Home({ t }) {
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  const now = new Date()
  const [period, setPeriod] = useState({ year: now.getFullYear(), month: now.getMonth() })
  const [transactions, setTransactions] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [news, setNews] = useState([])
  const [market, setMarket] = useState({ key_rate: null, usd: null, eur: null, labels: {} })
  const [selectedDay, setSelectedDay] = useState(null)
  const [editingTransactionId, setEditingTransactionId] = useState(null)
  const [form, setForm] = useState({ kind: 'expense', amount: '', description: '', category: '' })
  const [saving, setSaving] = useState(false)

  const days = useMemo(() => {
    const count = new Date(period.year, period.month + 1, 0).getDate()
    return Array.from({ length: count }, (_, index) => index + 1)
  }, [period])

  // Month Label using locale-sensitive formatting 
  const monthLabel = new Intl.DateTimeFormat(
    t.locale === 'ru' ? 'ru-RU' : 'en-US',
    { month: 'long' }
  ).format(new Date(period.year, period.month, 1))

  const dailyTotals = useMemo(() => {
    const totals = Object.fromEntries(days.map(day => [day, { income: 0, expense: 0 }]))
    transactions.forEach(transaction => {
      const day = Number(transaction.entry_date.slice(8, 10))
      if (totals[day]) totals[day][transaction.kind] += Number(transaction.amount)
    })
    return totals
  }, [days, transactions])

  const totalIncome = useMemo(
    () => transactions.filter(item => item.kind === 'income').reduce((sum, item) => sum + Number(item.amount), 0),
    [transactions]
  )

  const totalExpense = useMemo(
    () => transactions.filter(item => item.kind === 'expense').reduce((sum, item) => sum + Number(item.amount), 0),
    [transactions]
  )

  const maxAmount = Math.max(
    1,
    ...Object.values(dailyTotals).flatMap(total => [total.income, total.expense])
  )

  const changeMonth = (offset) => {
    setError('')
    setPeriod(current => {
      const next = new Date(current.year, current.month + offset, 1)
      return { year: next.getFullYear(), month: next.getMonth() }
    })
    setSelectedDay(null)
  }

  useEffect(() => {
    api.getProfile()
      .then(readResponse)
      .then(data => { if (data.username) setUsername(data.username) })
      .catch(error => setError(error.message))

    api.getTransactions(period.year, period.month + 1)
      .then(readResponse)
      .then(setTransactions)
      .catch(error => setError(error.message))

    api.getRecommendations(t.locale)
      .then(readResponse)
      .then(data => {
        setRecommendations(data.items || [])
        setNews(data.news || [])
        setMarket(data.market || { key_rate: null, usd: null, eur: null, labels: {} })
      })
      .catch(() => {
        setRecommendations([])
        setNews([])
        setMarket({ key_rate: null, usd: null, eur: null, labels: {} })
      })
  }, [period, t.locale])

  useEffect(() => {
    const reloadRecommendations = () => {
      api.getProfile()
        .then(readResponse)
        .then(data => { if (data.username) setUsername(data.username) })
        .catch(error => setError(error.message))
      api.getRecommendations(t.locale)
        .then(readResponse)
        .then(data => {
          setRecommendations(data.items || [])
          setNews(data.news || [])
          setMarket(data.market || { key_rate: null, usd: null, eur: null, labels: {} })
        })
        .catch(() => {
          setRecommendations([])
          setNews([])
          setMarket({ key_rate: null, usd: null, eur: null, labels: {} })
        })
    }

    window.addEventListener('profile-updated', reloadRecommendations)
    return () => window.removeEventListener('profile-updated', reloadRecommendations)
  }, [t.locale])

  const dayTransactions = useMemo(() => {
    if (selectedDay === null) return []
    const selectedDate = `${period.year}-${String(period.month + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`
    return transactions
      .filter(item => item.entry_date === selectedDate)
      .sort((a, b) => a.id - b.id)
  }, [selectedDay, period, transactions])

  const openEntry = (day) => {
    setSelectedDay(day)
    setEditingTransactionId(null)
    setForm({ kind: 'expense', amount: '', description: '', category: 'Housing' })
  }

  const startEditTransaction = (transaction) => {
    setSelectedDay(Number(transaction.entry_date.slice(8, 10)))
    setEditingTransactionId(transaction.id)
    setForm({
      kind: transaction.kind,
      amount: String(transaction.amount),
      description: transaction.description || '',
      category: transaction.category || '',
    })
  }

  const closeEntryPanel = () => {
    setSelectedDay(null)
    setEditingTransactionId(null)
    setForm({ kind: 'expense', amount: '', description: '', category: 'Housing' })
  }

  const selectedCategoryOptions = CATEGORY_OPTIONS[form.kind] || CATEGORY_OPTIONS.expense

  const saveEntry = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const entryDate = `${period.year}-${String(period.month + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`
      const payload = {
        entry_date: entryDate,
        kind: form.kind,
        amount: Number(form.amount),
        currency: 'RUB',
        category: form.category || undefined,
        description: form.description || undefined,
      }

      const transaction = editingTransactionId
        ? await readResponse(await api.updateTransaction(editingTransactionId, payload))
        : await readResponse(await api.addTransaction(payload))

      setTransactions(current => {
        if (editingTransactionId) {
          return current.map(item => (item.id === transaction.id ? transaction : item))
        }
        return [...current, transaction]
      })
      closeEntryPanel()
    } catch (error) {
      setError(error.message)
    } finally {
      setSaving(false)
    }
  }

  const removeTransaction = async (transactionId) => {
    setError('')
    try {
      const response = await api.deleteTransaction(transactionId)
      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || 'Delete failed')
      }
      setTransactions(current => current.filter(item => item.id !== transactionId))
      if (dayTransactions.length <= 1) {
        closeEntryPanel()
      }
    } catch (error) {
      setError(error.message)
    }
  }

  return (
    <div className="home-page">
      <div className="home-content">
        <p className="home-kicker">Fina</p>
        <h1>{t.home_welcome}, {username || t.home_user}!</h1>
        <p className="home-message">{t.home_message}</p>
        {error && <p className="error">{error}</p>}


        {/* Section: Finance Month */}
        <section className="finance-month" aria-labelledby="finance-month-title">
          <div className="finance-month-header">
            <div>
              <p className="finance-eyebrow">{t.home_finance_eyebrow}</p>
              <h2 id="finance-month-title">{monthLabel} <span>{period.year}</span></h2>
            </div>
            <div className="month-controls">
              <button type="button" onClick={() => changeMonth(-1)} aria-label={t.home_previous_month}>←</button>
              <button type="button" onClick={() => changeMonth(1)} aria-label={t.home_next_month}>→</button>
            </div>
          </div>
          {(market.key_rate !== null || market.usd !== null || market.eur !== null) && (
            <div className="market-strip">
              <div className="market-strip-head">
                <span>{t.locale === 'ru' ? 'Макро-метрики' : 'Macro indicators'}</span>
              </div>
              <div className="market-values">
                <div className="market-metric">
                  <span>{market.labels.key_rate || (t.locale === 'ru' ? 'Ключевая ставка' : 'Key rate')}</span>
                  <strong>{market.key_rate !== null ? `${market.key_rate}%` : '—'}</strong>
                </div>
                <div className="market-metric">
                  <span>USD/RUB</span>
                  <strong>{market.usd !== null ? market.usd.toFixed(2) : '—'}</strong>
                </div>
                <div className="market-metric">
                  <span>EUR/RUB</span>
                  <strong>{market.eur !== null ? market.eur.toFixed(2) : '—'}</strong>
                </div>
              </div>
              <div className="market-sparkline" aria-hidden="true">
                <span style={{ height: '30%' }} />
                <span style={{ height: '42%' }} />
                <span style={{ height: '55%' }} />
                <span style={{ height: '68%' }} />
                <span style={{ height: '48%' }} />
                <span style={{ height: '72%' }} />
                <span style={{ height: '85%' }} />
                <span style={{ height: '76%' }} />
                <span style={{ height: '88%' }} />
                <span style={{ height: '92%' }} />
              </div>
            </div>
          )}
          <div className="finance-summary">
            <div className="summary-pill income-pill">
              <span className="summary-label">{t.home_income}</span>
              <strong>{totalIncome.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽</strong>
            </div>
            <div className="summary-pill expense-pill">
              <span className="summary-label">{t.home_expenses}</span>
              <strong>{totalExpense.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽</strong>
            </div>
          </div>
          <div className="finance-legend">
            <span><i className="legend-income" />{t.home_income}</span>
            <span><i className="legend-expense" />{t.home_expenses}</span>
          </div>
          <div className="bar-chart-wrap">
            <div className="bar-chart">
              {days.map(day => {
                const total = dailyTotals[day]
                return (
                  <div className="bar-day" key={day}>
                    <div className="day-values">
                      {total.income > 0 && <span className="day-value income-value">{Math.round(total.income)}</span>}
                      {total.expense > 0 && <span className="day-value expense-value">{Math.round(total.expense)}</span>}
                    </div>
                    <div className="bars" title={`${day}: ${total.income} / ${total.expense}`}>
                      <span className="bar income" style={{ height: `${total.income / maxAmount * 100}%` }} />
                      <span className="bar expense" style={{ height: `${total.expense / maxAmount * 100}%` }} />
                    </div>
                    <span className="day-number">{day}</span>
                    <button type="button" className="add-entry" onClick={() => openEntry(day)} aria-label={`${t.home_add} ${day}`}>
                      +
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {selectedDay && (
            <div className="transaction-panel">
              <div className="transaction-panel-header">
                <strong>{selectedDay} {monthLabel}</strong>
                <button type="button" onClick={closeEntryPanel} aria-label={t.home_cancel}>×</button>
              </div>

              {dayTransactions.length > 0 && (
                <div className="day-transactions-list">
                  {dayTransactions.map(transaction => (
                    <div key={transaction.id} className="day-transaction-item">
                      <div className="day-transaction-main">
                        <span className={`transaction-kind ${transaction.kind}`}>{transaction.kind}</span>
                        <span className="transaction-amount">{Number(transaction.amount).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽</span>
                      </div>
                      <div className="day-transaction-meta">
                        {transaction.category && (
                            <span>
                              {t[`category_${transaction.category}`] || transaction.category}
                            </span>
                          )}
                        {transaction.description && <span>{transaction.description}</span>}
                      </div>
                      <div className="day-transaction-actions">
                        <button type="button" className="mini-button edit" onClick={() => startEditTransaction(transaction)}>Edit</button>
                        <button type="button" className="mini-button delete" onClick={() => removeTransaction(transaction.id)}>Delete</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <form className="transaction-form" onSubmit={saveEntry}>
                <div className="transaction-form-title">
                  <strong>{editingTransactionId ? 'Edit entry' : t.home_add} {selectedDay} {monthLabel}</strong>
                </div>
                <div className="transaction-fields">
                  <select value={form.kind} onChange={event => {
                    const nextKind = event.target.value
                    const nextCategory = CATEGORY_OPTIONS[nextKind][0]
                    setForm({ ...form, kind: nextKind, category: nextCategory })
                  }}>
                    <option value="expense">{t.home_expense}</option>
                    <option value="income">{t.home_income}</option>
                  </select>
                  <input type="number" min="0.01" step="0.01" placeholder={t.home_amount} value={form.amount} onChange={event => setForm({ ...form, amount: event.target.value })} required />
                  <select value={form.category || selectedCategoryOptions[0]} onChange={event => setForm({ ...form, category: event.target.value })}>
                    {selectedCategoryOptions.map(option => (
                      <option key={option} value={option}>
                        {t[`category_${option}`]}
                      </option>
                    ))}
                  </select>
                  <input type="text" maxLength="200" placeholder={t.home_note} value={form.description} onChange={event => setForm({ ...form, description: event.target.value })} />
                  <button type="submit" disabled={saving}>{saving ? t.home_saving : editingTransactionId ? 'Save' : t.home_save}</button>
                </div>
              </form>
            </div>
          )}
        </section>

        {recommendations.length > 0 && (
          <section className="recommendation-panel">
            <div className="recommendation-header">
              <p className="finance-eyebrow">{t.home_recommendations_subtitle}</p>
              <h3>{t.home_recommendations_title}</h3>
            </div>
            <div className="recommendation-list">
              {recommendations.map((item, index) => (
                <div key={`${item.title}-${index}`} className={`recommendation-item priority-${item.priority || 'medium'}`}>
                  <span className="recommendation-badge">{item.priority || 'medium'}</span>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {news.length > 0 && (
          <section className="news-panel">
            <div className="recommendation-header">
              <p className="finance-eyebrow">{t.locale === 'ru' ? 'Новости' : 'Finance news'}</p>
              <h3>{t.locale === 'ru' ? 'Макрообзор' : 'Market updates'}</h3>
            </div>
            <div className="news-list">
              {news.map((item, index) => (
                <a key={`${item.title}-${index}`} href={item.url} target="_blank" rel="noreferrer" className="news-item">
                  <span className="news-source">{item.source}</span>
                  <strong>{item.title}</strong>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* Section: Finance Month
        <section className="finance-month" aria-labelledby="finance-month-title">
          <div className="finance-month-header">
            <div>
              <p className="finance-eyebrow">{t.home_finance_eyebrow}</p>
              <h2 id="finance-month-title">{monthLabel} <span>{period.year}</span></h2>
            </div>

          </div>
          </section> */}

      </div>
    </div>
  )
}
