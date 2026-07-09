'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { transactionsApi, stocksApi } from '@/lib/api'
import { Transaction, Stock } from '@/types'
import { Plus, Trash2, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { fmtSGD } from '@/lib/utils'

const BROKERS = ['SCB', 'Moomoo', 'Tiger', 'IBKR', 'CDP', 'Other']

function AddTransactionModal({
  onClose,
  stocks,
}: {
  onClose: () => void
  stocks: Stock[]
}) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    ticker: '',
    companyName: '',
    date: new Date().toISOString().slice(0, 10),
    price: '',
    quantity: '',
    commission: '0',
    currency: 'SGD',
    market: 'SGX',
    category: 'Equity',
    broker: 'SCB',
    notes: '',
    type: 'BUY',
  })

  const mutation = useMutation({
    mutationFn: () => transactionsApi.add({
      ...form,
      price: parseFloat(form.price),
      quantity: parseFloat(form.quantity),
      commission: parseFloat(form.commission),
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] })
      qc.invalidateQueries({ queryKey: ['portfolio-tracker'] })
      toast.success('Transaction added')
      onClose()
    },
    onError: () => toast.error('Failed to add transaction'),
  })

  function handleTickerChange(ticker: string) {
    const stock = stocks.find(s => s.ticker === ticker)
    setForm(f => ({
      ...f,
      ticker,
      companyName: stock?.companyName ?? '',
      category: stock?.category ?? 'Equity',
      market: (stock as Stock & { market?: string })?.market ?? 'SGX',
      currency: (stock as Stock & { currency?: string })?.currency ?? 'SGD',
    }))
  }

  const set = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }))
  const totalCost = (parseFloat(form.price) || 0) * (parseFloat(form.quantity) || 0) + (parseFloat(form.commission) || 0)

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#132337] border border-[#C9A84C33] rounded-xl w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-white/10">
          <h2 className="text-lg font-bold text-white">Add Transaction</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <div className="p-5 space-y-4">
          {/* Ticker */}
          <div>
            <label className="stat-label block mb-1">Stock</label>
            <select
              value={form.ticker}
              onChange={e => handleTickerChange(e.target.value)}
              className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
            >
              <option value="">Select a stock...</option>
              {stocks.map(s => (
                <option key={s.ticker} value={s.ticker}>
                  {s.ticker} — {s.companyName}
                </option>
              ))}
            </select>
          </div>

          {/* Date and Type */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="stat-label block mb-1">Buy Date</label>
              <input
                type="date"
                value={form.date}
                onChange={e => set('date', e.target.value)}
                className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
              />
            </div>
            <div>
              <label className="stat-label block mb-1">Broker</label>
              <select
                value={form.broker}
                onChange={e => set('broker', e.target.value)}
                className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
              >
                {BROKERS.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          </div>

          {/* Price and Quantity */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="stat-label block mb-1">
                Buy Price ({form.currency})
              </label>
              <input
                type="number"
                step="0.001"
                placeholder="0.00"
                value={form.price}
                onChange={e => set('price', e.target.value)}
                className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
              />
            </div>
            <div>
              <label className="stat-label block mb-1">Shares / Units</label>
              <input
                type="number"
                step="1"
                placeholder="100"
                value={form.quantity}
                onChange={e => set('quantity', e.target.value)}
                className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
              />
            </div>
          </div>

          {/* Commission */}
          <div>
            <label className="stat-label block mb-1">
              Commission / Fees ({form.currency})
            </label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={form.commission}
              onChange={e => set('commission', e.target.value)}
              className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="stat-label block mb-1">Notes (optional)</label>
            <input
              type="text"
              placeholder="e.g. Added on dip, DCA buy"
              value={form.notes}
              onChange={e => set('notes', e.target.value)}
              className="w-full bg-[#0B1929] border border-[#C9A84C22] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#C9A84C]"
            />
          </div>

          {/* Total cost preview */}
          {totalCost > 0 && (
            <div className="bg-[#0B1929] rounded-lg p-3 border border-[#C9A84C22]">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Total Cost</span>
                <span className="text-[#E2C06E] font-bold">
                  {form.currency} {totalCost.toLocaleString('en-SG', { maximumFractionDigits: 2 })}
                </span>
              </div>
              {form.price && form.quantity && (
                <div className="flex justify-between text-xs mt-1">
                  <span className="text-slate-600">
                    {form.quantity} shares × {form.currency} {form.price}
                  </span>
                  <span className="text-slate-600">
                    + {form.currency} {form.commission} commission
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-5 border-t border-white/10">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 text-sm text-slate-400 hover:text-white border border-white/10 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={!form.ticker || !form.price || !form.quantity || mutation.isPending}
            className="flex-1 px-4 py-2 text-sm font-semibold bg-[#C9A84C] hover:bg-[#E2C06E] disabled:opacity-40 text-black rounded-lg transition-colors"
          >
            {mutation.isPending ? 'Saving...' : 'Add Transaction'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function TransactionsPage() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)

  const { data: transactions = [] } = useQuery<Transaction[]>({
    queryKey: ['transactions'],
    queryFn: transactionsApi.list,
  })

  const { data: stocks = [] } = useQuery<Stock[]>({
    queryKey: ['stocks'],
    queryFn: stocksApi.list,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => transactionsApi.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] })
      qc.invalidateQueries({ queryKey: ['portfolio-tracker'] })
      toast.success('Transaction deleted')
    },
  })

  // Group by ticker
  const byTicker = transactions.reduce((acc, t) => {
    if (!acc[t.ticker]) acc[t.ticker] = []
    acc[t.ticker].push(t)
    return acc
  }, {} as Record<string, Transaction[]>)

  const totalInvested = transactions.reduce((sum, t) => {
    return sum + (t.price * t.quantity) + (t.commission || 0)
  }, 0)

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Transactions</h1>
          <p className="text-slate-400 text-sm mt-1">
            {transactions.length} transactions · {Object.keys(byTicker).length} stocks ·
            Total invested: <span className="text-[#C9A84C]">{fmtSGD(totalInvested)}</span>
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#C9A84C] hover:bg-[#E2C06E] text-black text-sm font-semibold rounded-lg transition-colors"
        >
          <Plus size={14} /> Add Transaction
        </button>
      </div>

      {/* Transactions table */}
      {transactions.length === 0 ? (
        <div className="card text-center py-20">
          <p className="text-slate-400 text-lg mb-2">No transactions yet</p>
          <p className="text-sm text-slate-600 mb-6">
            Add your first buy transaction to start tracking your real portfolio
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="px-6 py-2.5 bg-[#C9A84C] hover:bg-[#E2C06E] text-black text-sm font-semibold rounded-lg"
          >
            Add First Transaction
          </button>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs uppercase tracking-widest border-b border-white/5">
                <th className="text-left py-3 px-4">Date</th>
                <th className="text-left py-3 px-4">Stock</th>
                <th className="text-right py-3 px-4">Price</th>
                <th className="text-right py-3 px-4">Shares</th>
                <th className="text-right py-3 px-4">Commission</th>
                <th className="text-right py-3 px-4">Total Cost</th>
                <th className="text-left py-3 px-4">Broker</th>
                <th className="text-left py-3 px-4">Notes</th>
                <th className="py-3 px-4"></th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t, i) => {
                const cost = (t.price * t.quantity) + (t.commission || 0)
                return (
                  <tr
                    key={t.id}
                    className={`border-b border-white/5 hover:bg-white/2 transition-colors ${i % 2 === 0 ? '' : 'bg-white/1'}`}
                  >
                    <td className="py-3 px-4 text-slate-400 font-mono text-xs">
                      {t.date}
                    </td>
                    <td className="py-3 px-4">
                      <p className="text-white font-medium">{t.companyName}</p>
                      <p className="text-slate-500 text-xs font-mono">{t.ticker}</p>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-300">
                      {t.currency} {t.price.toLocaleString('en-SG', { minimumFractionDigits: 3 })}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-300">
                      {t.quantity.toLocaleString('en-SG')}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-500 text-xs">
                      {t.commission > 0 ? `${t.currency} ${t.commission}` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-[#E2C06E] font-semibold">
                      {t.currency} {cost.toLocaleString('en-SG', { maximumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-xs">
                      {t.broker || '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-500 text-xs max-w-32 truncate">
                      {t.notes || '—'}
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => deleteMutation.mutate(t.id)}
                        className="text-red-500/40 hover:text-red-400 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <AddTransactionModal
          onClose={() => setShowModal(false)}
          stocks={stocks}
        />
      )}
    </div>
  )
}