'use client'

import { useLatestSignals, useRunScreener } from '@/hooks/useSDAS'
import { SignalCard } from '@/components/ui/SignalCard'
import { YieldChart } from '@/components/charts/YieldChart'
import { SignalType } from '@/types'
import { RefreshCw } from 'lucide-react'

export default function SignalsPage() {
  const { data: signals = [], isLoading } = useLatestSignals()
  const screenerMutation = useRunScreener()

  const bySignal = (type: SignalType) => signals.filter(s => s.signal === type)
  const date = signals[0]?.date ?? null

  const chartData = signals.map(s => ({
    ticker: s.ticker,
    yield: s.yield,
    signal: s.signal,
  }))

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-slate-400">
          <RefreshCw size={16} className="animate-spin" />
          Loading signals...
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Daily Signals</h1>
          <p className="text-slate-400 text-sm mt-1">
            {date ? `Last screened: ${date}` : 'No screener data yet'}
          </p>
        </div>
        <button
          onClick={() => screenerMutation.mutate(true)}
          disabled={screenerMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-[#C9A84C] hover:bg-[#E2C06E] disabled:opacity-50 text-black text-sm font-semibold rounded-lg transition-colors"
        >
          <RefreshCw size={14} className={screenerMutation.isPending ? 'animate-spin' : ''} />
          {screenerMutation.isPending ? 'Running...' : 'Run Now'}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card border-green-800/40 bg-green-900/10 text-center py-4">
          <p className="text-3xl font-bold text-green-400">{bySignal('BUY_NOW').length}</p>
          <p className="stat-label mt-1">Buy Now</p>
        </div>
        <div className="card border-amber-800/40 bg-amber-900/10 text-center py-4">
          <p className="text-3xl font-bold text-amber-400">{bySignal('WATCHLIST').length}</p>
          <p className="stat-label mt-1">Watchlist</p>
        </div>
        <div className="card border-red-800/40 bg-red-900/10 text-center py-4">
          <p className="text-3xl font-bold text-red-400">{bySignal('OVERVALUED').length}</p>
          <p className="stat-label mt-1">Overvalued</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="card mb-8">
          <p className="stat-label mb-4">Dividend Yield by Stock</p>
          <YieldChart data={chartData} minYield={4} />
          <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-500 inline-block" /> Buy Now</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> Watchlist</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> Overvalued</span>
          </div>
        </div>
      )}

      {bySignal('BUY_NOW').length > 0 && (
        <section className="mb-8">
          <h2 className="text-base font-semibold text-green-400 mb-3">
            🟢 Buy Now <span className="text-xs text-green-700 font-normal">— SGD 750 per position</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {bySignal('BUY_NOW').map(s => <SignalCard key={s.ticker} signal={s} />)}
          </div>
        </section>
      )}

      {bySignal('WATCHLIST').length > 0 && (
        <section className="mb-8">
          <h2 className="text-base font-semibold text-amber-400 mb-3">
            🟡 Watchlist <span className="text-xs text-amber-700 font-normal">— SGD 500 per position</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {bySignal('WATCHLIST').map(s => <SignalCard key={s.ticker} signal={s} />)}
          </div>
        </section>
      )}

      {bySignal('OVERVALUED').length > 0 && (
        <section>
          <h2 className="text-base font-semibold text-red-400 mb-3">🔴 Overvalued / Skip</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {bySignal('OVERVALUED').map(s => <SignalCard key={s.ticker} signal={s} />)}
          </div>
        </section>
      )}

      {signals.length === 0 && (
        <div className="card text-center py-20">
          <p className="text-slate-400 text-lg mb-2">No signals yet</p>
          <p className="text-sm text-slate-600">
            Click Run Now or wait for the 7:15 PM SGT schedule.
          </p>
        </div>
      )}
    </div>
  )
}
