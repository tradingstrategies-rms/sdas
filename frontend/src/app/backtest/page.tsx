'use client'

import { useState } from 'react'
import { backtestApi } from '@/lib/api'
import { BacktestResult } from '@/types'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import toast from 'react-hot-toast'

const DEFAULT_PARAMS = {
  startDate: '2020-01-01',
  endDate: '2024-12-31',
  initialCash: 10000,
  monthlyContribution: 1000,
  buyNowAmount: 750,
  watchlistAmount: 500,
}

export default function BacktestPage() {
  const [params, setParams] = useState(DEFAULT_PARAMS)
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleRun() {
    setLoading(true)
    try {
      const res = await backtestApi.run(params)
      if (res.error) throw new Error(res.error)
      setResult(res)
    } catch (e: unknown) {
      toast.error('Backtest failed: ' + (e instanceof Error ? e.message : 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  const set = (key: string, val: string | number) => setParams(p => ({ ...p, [key]: val }))

  return (
    <div className="p-8 max-w-5xl">
      <h1 className="text-2xl font-bold text-white mb-2">Backtest Engine</h1>
      <p className="text-slate-400 text-sm mb-8">
        Simulate the SDAS strategy on historical SGX data.
      </p>

      {/* Parameters */}
      <div className="card mb-6">
        <h2 className="text-sm font-semibold text-[#C9A84C] uppercase tracking-widest mb-4">Parameters</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[
            { key: 'startDate', label: 'Start Date', type: 'date' },
            { key: 'endDate', label: 'End Date', type: 'date' },
            { key: 'initialCash', label: 'Initial Cash (SGD)', type: 'number' },
            { key: 'monthlyContribution', label: 'Monthly Contribution (SGD)', type: 'number' },
            { key: 'buyNowAmount', label: 'BUY NOW Amount (SGD)', type: 'number' },
            { key: 'watchlistAmount', label: 'WATCHLIST Amount (SGD)', type: 'number' },
          ].map(({ key, label, type }) => (
            <div key={key}>
              <label className="stat-label block mb-1">{label}</label>
              <input
                type={type}
                value={(params as Record<string, unknown>)[key] as string}
                onChange={e => set(key, type === 'number' ? Number(e.target.value) : e.target.value)}
                className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
              />
            </div>
          ))}
        </div>

        <button
          onClick={handleRun}
          disabled={loading}
          className="mt-5 px-6 py-2.5 bg-[#C9A84C] hover:bg-[#E2C06E] disabled:opacity-50 text-black text-sm font-semibold rounded-lg transition-colors"
        >
          {loading ? 'Running backtest…' : 'Run Backtest'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              { label: 'CAGR', value: `${result.cagr.toFixed(1)}%` },
              { label: 'Final Value', value: `SGD ${result.portfolioValue.toLocaleString('en-SG', { maximumFractionDigits: 0 })}` },
              { label: 'Total Invested', value: `SGD ${result.totalInvested.toLocaleString('en-SG', { maximumFractionDigits: 0 })}` },
              { label: 'Annual Dividends', value: `SGD ${result.annualDividends.toLocaleString('en-SG', { maximumFractionDigits: 0 })}` },
              { label: 'Monthly Dividends', value: `SGD ${result.monthlyDividends.toLocaleString('en-SG', { maximumFractionDigits: 0 })}` },
              { label: 'Yield on Cost', value: `${result.yieldOnCost.toFixed(1)}%` },
              { label: 'Max Drawdown', value: `${result.maxDrawdown.toFixed(1)}%` },
              { label: 'Dividends Reinvested', value: `SGD ${result.dividendReinvestmentValue.toLocaleString('en-SG', { maximumFractionDigits: 0 })}` },
            ].map(({ label, value }) => (
              <div key={label} className="card text-center">
                <p className="stat-label">{label}</p>
                <p className="text-xl font-bold text-[#E2C06E] mt-1">{value}</p>
              </div>
            ))}
          </div>

          {/* Chart */}
          {result.portfolioHistory?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-[#C9A84C] uppercase tracking-widest mb-4">
                Portfolio Value Over Time
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={result.portfolioHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false}
                    tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ background: '#132337', border: '1px solid #C9A84C33', borderRadius: 8 }}
                    labelStyle={{ color: '#C9A84C' }}
                    itemStyle={{ color: '#fff' }}
                    formatter={(v: number) => [`SGD ${v.toLocaleString('en-SG', { maximumFractionDigits: 0 })}`, 'Value']}
                  />
                  <Line type="monotone" dataKey="value" stroke="#C9A84C" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  )
}
