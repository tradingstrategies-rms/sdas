'use client'

import { usePortfolio, useLatestSignals, useRunScreener } from '@/hooks/useSDAS'
import { StatCard } from '@/components/ui/StatCard'
import { fmtSGD, fmtPct, yearsToGoal } from '@/lib/utils'
import { TrendingUp, DollarSign, Percent, PiggyBank, Target, Clock, RefreshCw } from 'lucide-react'

const TARGET_MONTHLY = 5000

export default function DashboardPage() {
  const { data: portfolio } = usePortfolio()
  const { data: signals = [] } = useLatestSignals()
  const screenerMutation = useRunScreener()

  const p = portfolio ?? { totalInvested: 0, marketValue: 0, annualDividend: 0, monthlyDividend: 0, yieldOnCost: 0, cashReserve: 0 }
  const monthlyDiv = p.monthlyDividend
  const progressPct = Math.min((monthlyDiv / TARGET_MONTHLY) * 100, 100)
  const yrs = yearsToGoal(monthlyDiv)
  const latestDate = signals[0]?.date ?? null

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Portfolio Overview</h1>
          <p className="text-slate-400 text-sm mt-1">Singapore Dividend Accumulation Screener
            {latestDate && <span className="ml-2 text-slate-600">· Last run: {latestDate}</span>}
          </p>
        </div>
        <button onClick={() => screenerMutation.mutate()} disabled={screenerMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-[#C9A84C] hover:bg-[#E2C06E] disabled:opacity-50 text-black text-sm font-semibold rounded-lg transition-colors">
          {screenerMutation.isPending ? <RefreshCw size={14} className="animate-spin" /> : <Clock size={14} />}
          {screenerMutation.isPending ? 'Running...' : 'Run Screener Now'}
        </button>
      </div>

      {/* Goal progress */}
      <div className="card mb-6 border-[#C9A84C33]">
        <div className="flex items-end justify-between mb-4">
          <div>
            <p className="stat-label">Progress to SGD 5,000/month goal</p>
            <p className="text-3xl font-bold text-[#E2C06E] mt-2">
              {fmtSGD(monthlyDiv)}<span className="text-slate-500 text-base font-normal ml-1">/ month</span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-[#C9A84C]">{fmtPct(progressPct)}</p>
            <p className="text-xs text-slate-500 mt-1">of target</p>
          </div>
        </div>
        <div className="w-full bg-[#0B1929] rounded-full h-2.5 overflow-hidden">
          <div className="bg-gradient-to-r from-[#8B6F2F] via-[#C9A84C] to-[#E2C06E] h-2.5 rounded-full transition-all duration-700"
            style={{ width: `${progressPct}%` }} />
        </div>
        {yrs !== null && monthlyDiv > 0 && (
          <p className="text-xs text-slate-500 mt-2">~{yrs.toFixed(1)} years to goal at 12% dividend growth</p>
        )}
      </div>

      {/* Stat rows */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Portfolio Value" value={fmtSGD(p.marketValue)} icon={DollarSign} />
        <StatCard label="Total Invested" value={fmtSGD(p.totalInvested)} icon={TrendingUp} />
        <StatCard label="Annual Dividend" value={fmtSGD(p.annualDividend)} icon={Percent} />
        <StatCard label="Monthly Dividend" value={fmtSGD(monthlyDiv)} icon={PiggyBank} accent />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Yield on Cost" value={fmtPct(p.yieldOnCost, 2)} sub="based on cost" icon={Percent} />
        <StatCard label="Cash Reserve" value={fmtSGD(p.cashReserve)} sub="20% minimum" icon={PiggyBank} />
        <StatCard label="Years to Goal" value={yrs !== null ? `${yrs.toFixed(1)} yrs` : '—'} sub="12% dividend growth" icon={Target} />
        <StatCard label="Screened Stocks" value={signals.length > 0 ? `${signals.length}` : '—'} sub={latestDate ?? 'not yet run'} icon={Clock} />
      </div>

      {/* Signal summary */}
      {signals.length > 0 && (
        <div className="card">
          <p className="stat-label mb-4">Today's Signal Summary</p>
          <div className="grid grid-cols-3 gap-4 text-center">
            {(['BUY_NOW', 'WATCHLIST', 'OVERVALUED'] as const).map(type => {
              const count = signals.filter(s => s.signal === type).length
              const deploy = type === 'BUY_NOW' ? count * 750 : type === 'WATCHLIST' ? count * 500 : 0
              const color = type === 'BUY_NOW' ? 'text-green-400' : type === 'WATCHLIST' ? 'text-amber-400' : 'text-red-400'
              const emoji = type === 'BUY_NOW' ? '🟢' : type === 'WATCHLIST' ? '🟡' : '🔴'
              const label = type.replace('_', ' ')
              return (
                <div key={type}>
                  <p className={`text-2xl font-bold ${color}`}>{count}</p>
                  <p className={`text-xs mt-1 ${color.replace('400', '700')}`}>{emoji} {label}</p>
                  <p className="text-xs text-slate-600 mt-0.5">{deploy > 0 ? `SGD ${deploy} to deploy` : 'Skip today'}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
