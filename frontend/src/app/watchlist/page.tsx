'use client'
import { useQuery } from '@tanstack/react-query'
import { stocksApi, signalsApi } from '@/lib/api'
import { Stock, Signal } from '@/types'

export default function WatchlistPage() {
  const { data: stocks = [] } = useQuery<Stock[]>({ queryKey: ['stocks'], queryFn: stocksApi.list })
  const { data: signals = [] } = useQuery<Signal[]>({ queryKey: ['signals-latest'], queryFn: signalsApi.latest })

  const signalMap = Object.fromEntries(signals.map(s => [s.ticker, s]))

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-2">Watchlist</h1>
      <p className="text-slate-400 text-sm mb-8">All 14 monitored SGX dividend stocks.</p>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs uppercase tracking-widest border-b border-white/5">
              <th className="text-left py-3 px-4">Ticker</th>
              <th className="text-left py-3 px-4">Company</th>
              <th className="text-left py-3 px-4">Category</th>
              <th className="text-right py-3 px-4">Target Yield</th>
              <th className="text-right py-3 px-4">Latest Signal</th>
              <th className="text-right py-3 px-4">Score</th>
              <th className="text-right py-3 px-4">Yield</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((s: Stock) => {
              const sig = signalMap[s.ticker]
              const signalBadge = sig ? (
                sig.signal === 'BUY_NOW' ? <span className="badge-buy">🟢 BUY</span> :
                sig.signal === 'WATCHLIST' ? <span className="badge-watch">🟡 WATCH</span> :
                <span className="badge-over">🔴 OVER</span>
              ) : <span className="text-slate-600 text-xs">—</span>

              return (
                <tr key={s.ticker} className="border-b border-white/5 hover:bg-white/2 transition-colors">
                  <td className="py-3 px-4 font-mono text-[#C9A84C]">{s.ticker}</td>
                  <td className="py-3 px-4 text-white font-medium">{s.companyName}</td>
                  <td className="py-3 px-4 text-slate-400">{s.category}</td>
                  <td className="py-3 px-4 text-right text-slate-300">{s.targetYield}%</td>
                  <td className="py-3 px-4 text-right">{signalBadge}</td>
                  <td className="py-3 px-4 text-right text-slate-300 font-mono">{sig ? `${sig.score}/19` : '—'}</td>
                  <td className="py-3 px-4 text-right text-[#E2C06E] font-mono">
                    {sig ? `${sig.yield.toFixed(1)}%` : '—'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {stocks.length === 0 && (
          <p className="text-center text-slate-500 py-12">
            No stocks found. Go to Settings → Seed All 14 Stocks.
          </p>
        )}
      </div>
    </div>
  )
}
