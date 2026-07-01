'use client'

import { useState } from 'react'
import { stocksApi } from '@/lib/api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Stock } from '@/types'
import toast from 'react-hot-toast'
import { Trash2, Plus } from 'lucide-react'

const SEED_STOCKS: Stock[] = [
  { ticker: 'D05.SI', companyName: 'DBS Group', sector: 'Financials', category: 'Bank', targetYield: 5.0, active: true },
  { ticker: 'U11.SI', companyName: 'United Overseas Bank', sector: 'Financials', category: 'Bank', targetYield: 5.0, active: true },
  { ticker: 'Z74.SI', companyName: 'Singapore Telecommunications', sector: 'Communications', category: 'Equity', targetYield: 5.5, active: true },
  { ticker: 'S58.SI', companyName: 'SATS Ltd', sector: 'Industrials', category: 'Equity', targetYield: 4.5, active: true },
  { ticker: 'C07.SI', companyName: 'Jardine Cycle & Carriage', sector: 'Consumer', category: 'Equity', targetYield: 4.0, active: true },
  { ticker: '9CI.SI', companyName: 'CapitaLand Investment', sector: 'Real Estate', category: 'Equity', targetYield: 4.5, active: true },
  { ticker: 'A17U.SI', companyName: 'Ascendas REIT', sector: 'Industrial REIT', category: 'REIT', targetYield: 5.5, active: true },
  { ticker: 'C38U.SI', companyName: 'CapitaLand Integrated Commercial Trust', sector: 'Retail REIT', category: 'REIT', targetYield: 5.5, active: true },
  { ticker: 'AJBU.SI', companyName: 'Keppel Infrastructure Trust', sector: 'Infrastructure', category: 'Infrastructure', targetYield: 7.0, active: true },
  { ticker: 'HMN.SI', companyName: 'Frasers Centrepoint Trust', sector: 'Retail REIT', category: 'REIT', targetYield: 6.0, active: true },
  { ticker: 'M44U.SI', companyName: 'Mapletree Industrial Trust', sector: 'Industrial REIT', category: 'REIT', targetYield: 5.5, active: true },
  { ticker: 'C2PU.SI', companyName: 'Mapletree Pan Asia Commercial Trust', sector: 'Office REIT', category: 'REIT', targetYield: 6.5, active: true },
  { ticker: 'J69U.SI', companyName: 'Frasers Logistics & Commercial Trust', sector: 'Industrial REIT', category: 'REIT', targetYield: 6.5, active: true },
  { ticker: 'A7RU.SI', companyName: 'Keppel DC REIT', sector: 'Data Centre REIT', category: 'REIT', targetYield: 5.5, active: true },
]

const CATEGORY_COLORS: Record<string, string> = {
  Bank: 'badge-buy',
  REIT: 'badge-watch',
  Infrastructure: 'text-blue-400 bg-blue-900/30 border border-blue-700/30 px-2 py-0.5 rounded-full text-xs font-semibold',
  Equity: 'text-slate-400 bg-slate-800/60 border border-slate-700/30 px-2 py-0.5 rounded-full text-xs font-semibold',
}

export default function SettingsPage() {
  const qc = useQueryClient()
  const { data: stocks = [] } = useQuery<Stock[]>({ queryKey: ['stocks'], queryFn: stocksApi.list })

  const removeMutation = useMutation({
    mutationFn: (ticker: string) => stocksApi.remove(ticker),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['stocks'] }); toast.success('Stock removed') },
  })

  async function handleSeedStocks() {
    const promises = SEED_STOCKS.map(s => stocksApi.add(s))
    await Promise.all(promises)
    qc.invalidateQueries({ queryKey: ['stocks'] })
    toast.success('Seed stocks added to Firestore!')
  }

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
      <p className="text-slate-400 text-sm mb-8">Manage your watchlist and screener configuration.</p>

      {/* Watchlist */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-[#C9A84C] uppercase tracking-widest">Watchlist Stocks</h2>
          <button
            onClick={handleSeedStocks}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-[#C9A84C22] hover:bg-[#C9A84C33] text-[#C9A84C] rounded-lg transition-colors border border-[#C9A84C33]"
          >
            <Plus size={12} /> Seed All 14 Stocks
          </button>
        </div>

        {stocks.length === 0 ? (
          <p className="text-slate-500 text-sm py-4 text-center">
            No stocks in Firestore yet. Click "Seed All 14 Stocks" to get started.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs uppercase tracking-widest border-b border-white/5">
                <th className="text-left pb-2">Ticker</th>
                <th className="text-left pb-2">Company</th>
                <th className="text-left pb-2">Category</th>
                <th className="text-left pb-2">Target Yield</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((s: Stock) => (
                <tr key={s.ticker} className="border-b border-white/5 hover:bg-white/2">
                  <td className="py-2.5 font-mono text-[#C9A84C]">{s.ticker}</td>
                  <td className="py-2.5 text-white">{s.companyName}</td>
                  <td className="py-2.5">
                    <span className={CATEGORY_COLORS[s.category] ?? 'text-slate-400'}>{s.category}</span>
                  </td>
                  <td className="py-2.5 text-slate-300">{s.targetYield}%</td>
                  <td className="py-2.5 text-right">
                    <button
                      onClick={() => removeMutation.mutate(s.ticker)}
                      className="text-red-500/50 hover:text-red-400 transition-colors"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Info cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <h3 className="stat-label mb-2">Scoring Thresholds</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-400">BUY NOW (min score)</span><span className="text-green-400 font-mono">13 / 19</span></div>
            <div className="flex justify-between"><span className="text-slate-400">WATCHLIST (min score)</span><span className="text-amber-400 font-mono">9 / 19</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Min Dividend Yield</span><span className="text-white font-mono">4.0%</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Max Position Size</span><span className="text-white font-mono">15%</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Cash Reserve</span><span className="text-white font-mono">20%</span></div>
          </div>
        </div>
        <div className="card">
          <h3 className="stat-label mb-2">Investment Amounts</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-400">BUY NOW amount</span><span className="text-green-400 font-mono">SGD 750</span></div>
            <div className="flex justify-between"><span className="text-slate-400">WATCHLIST amount</span><span className="text-amber-400 font-mono">SGD 500</span></div>
            <div className="flex justify-between"><span className="text-slate-400">STI crash &gt;10%</span><span className="text-white font-mono">SGD 1,000 extra</span></div>
            <div className="flex justify-between"><span className="text-slate-400">STI crash &gt;20%</span><span className="text-white font-mono">50% cash reserve</span></div>
            <div className="flex justify-between"><span className="text-slate-400">STI crash &gt;30%</span><span className="text-white font-mono">100% cash reserve</span></div>
          </div>
        </div>
      </div>
    </div>
  )
}
