import { useEffect, useMemo, useState } from 'react'
import { api, readResponse } from '../api'

export default function Home({ t }) {
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  const now = new Date()
  const [period, setPeriod] = useState({ year: now.getFullYear(), month: now.getMonth() })
  const [transactions, setTransactions] = useState([])
  const [selectedDay, setSelectedDay] = useState(null)
  const [form, setForm] = useState({ kind: 'expense', amount: '', description: '' })
  const [saving, setSaving] = useState(false)

  const days = useMemo(() => {
    const count = new Date(period.year, period.month + 1, 0).getDate()
    return Array.from({ length: count }, (_, index) => index + 1)
  }, [period])

  const monthLabel = new Intl.DateTimeFormat(undefined, { month: 'long' }).format(
    new Date(period.year, period.month, 1)
  )

  const dailyTotals = useMemo(() => {
    const totals = Object.fromEntries(days.map(day => [day, { income: 0, expense: 0 }]))
    transactions.forEach(transaction => {
      const day = Number(transaction.entry_date.slice(8, 10))
      if (totals[day]) totals[day][transaction.kind] += Number(transaction.amount)
    })
    return totals
  }, [days, transactions])

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
  }, [])

  useEffect(() => {
    api.getTransactions(period.year, period.month + 1)
      .then(readResponse)
      .then(setTransactions)
      .catch(error => setError(error.message))
  }, [period])

  const openEntry = (day) => {
    setSelectedDay(day)
    setForm({ kind: 'expense', amount: '', description: '' })
  }

  const saveEntry = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const entryDate = `${period.year}-${String(period.month + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`
      const transaction = await readResponse(await api.addTransaction({
        entry_date: entryDate,
        kind: form.kind,
        amount: Number(form.amount),
        description: form.description || undefined,
      }))
      setTransactions(current => [...current, transaction])
      setSelectedDay(null)
    } catch (error) {
      setError(error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="home-page">
      <div className="home-content">
        <p className="home-kicker">Fina</p>
        <h1>{t.home_welcome}, {username || t.home_user}!</h1>
        <p className="home-message">{t.home_message}</p>
        {error && <p className="error">{error}</p>}

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
          <div className="finance-legend">
            <span><i className="legend-income" />{t.home_income}</span>
            <span><i className="legend-expense" />{t.home_expenses}</span>
          </div>
          <div className="bar-chart">
            {days.map(day => {
              const total = dailyTotals[day]
              return (
                <div className="bar-day" key={day}>
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
          {selectedDay && (
            <form className="transaction-form" onSubmit={saveEntry}>
              <div className="transaction-form-title">
                <strong>{t.home_add} {selectedDay} {monthLabel}</strong>
                <button type="button" onClick={() => setSelectedDay(null)} aria-label={t.home_cancel}>×</button>
              </div>
              <div className="transaction-fields">
                <select value={form.kind} onChange={event => setForm({ ...form, kind: event.target.value })}>
                  <option value="expense">{t.home_expense}</option>
                  <option value="income">{t.home_income}</option>
                </select>
                <input type="number" min="0.01" step="0.01" placeholder={t.home_amount} value={form.amount} onChange={event => setForm({ ...form, amount: event.target.value })} required />
                <input type="text" maxLength="200" placeholder={t.home_note} value={form.description} onChange={event => setForm({ ...form, description: event.target.value })} />
                <button type="submit" disabled={saving}>{saving ? t.home_saving : t.home_save}</button>
              </div>
            </form>
          )}
        </section>
      </div>
    </div>
  )
}