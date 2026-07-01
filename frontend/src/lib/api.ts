/**
 * Axios API client — points at the FastAPI backend.
 */
import axios from 'axios'

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Stocks ─────────────────────────────────────────────────────────────────────
export const stocksApi = {
  list: () => api.get('/api/v1/stocks/').then(r => r.data),
  add: (data: object) => api.post('/api/v1/stocks/', data).then(r => r.data),
  remove: (ticker: string) => api.delete(`/api/v1/stocks/${ticker}`).then(r => r.data),
}

// ── Signals ────────────────────────────────────────────────────────────────────
export const signalsApi = {
  latest: () => api.get('/api/v1/signals/latest').then(r => r.data),
  byDate: (date: string) => api.get(`/api/v1/signals/date/${date}`).then(r => r.data),
  history: (ticker: string) => api.get(`/api/v1/signals/${ticker}/history`).then(r => r.data),
}

// ── Portfolio ──────────────────────────────────────────────────────────────────
export const portfolioApi = {
  get: () => api.get('/api/v1/portfolio/').then(r => r.data),
  update: (data: object) => api.put('/api/v1/portfolio/', data).then(r => r.data),
}

// ── Screener ───────────────────────────────────────────────────────────────────
export const screenerApi = {
  run: (sendEmail = true) =>
    api.post(`/api/v1/screener/run?send_email=${sendEmail}`).then(r => r.data),
}

// ── Backtest ───────────────────────────────────────────────────────────────────
export const backtestApi = {
  run: (params: object) => api.post('/api/v1/backtest/run', params).then(r => r.data),
}
