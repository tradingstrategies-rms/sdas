'use client'

import { useQuery } from '@tanstack/react-query'
import { transactionsApi } from '@/lib/api'
import { useLatestSignals, useRunScreener } from '@/hooks/useSDAS'
import { PortfolioData } from '@/types'
import { fmtSGD, fmtPct } from '@/lib/utils'
import { TrendingUp, TrendingDown, DollarSign, Percent, PiggyBank, Target, RefreshCw, Clock } from 'lucide-react'

const TARGET_MONTHLY = 5000

function StatCard({ label, value, sub, accent = false, positive, icon: Icon }: {
  label: string; value: string; sub?: string; accent?: boolean
  positive?: boolean; icon?: React.ElementType
}) {
  return (
    <div className={`card ${accent ? 'border-[#C9A84C55]' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="stat-label">{label}</p>
          <p className={`stat-value mt-1 ${accent ? 'text-[#E2C06E]' : positive === true ? 'text-green-400' : positive === false ? 'text-red-400' : 'text-white'}`}>
            {value}
          </p>
          {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
        </div>
        {Icon && (
          <div className={`p-2 rounded-lg shrink-0 ml-3 ${accent ? 'bg-[#C9A84C22]' : 'bg-white/5'}`}>
            <Icon size={18} className={accent ? 'text-[#C9A84C]' : 'text-slate-400'} />
          </div>
        )}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: portfolio, isLoading } = useQuery<PortfolioData>({
    queryKey: ['portfolio-tracker'],
    queryFn: transactionsApi.portfolio,
    staleTime: 2 * 60_000,
  })

  const { data: signals = [] } = useLatestSignals()
  const screenerMutation = useRunScreener()

  const p = portfolio ?? {
    totalInvested: 0, marketValue: 0, unrealisedPL: 0,
    annualDividend: 0, monthlyDividend: 0, yieldOnCost: 0,
    cashReserve: 0, progressPct: 0, holdingsCount: 0,
    targetMonthly: TARGET_MONTHLY, holdings: [],
  }

  const latestDate = signals[0]?.date ?? null
  const progressPct = p.progressPct ?? 0

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-slate-400">
          <RefreshCw size={16} className="animate-spin" />
          Loading portfolio...
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Portfolio Overview</h1>
          <p className="text-slate-400 text-sm mt-1">
            {p.holdingsCount} holdings
            {latestDate && <span className="ml-2 text-slate-600">· Last screened: {latestDate}</span>}
          </p>
        </div>
        <button
          onClick={() => screenerMutation.mutate()}
          disabled={screenerMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-[#C9A84C] hover:bg-[#E2C06E] disabled:opacity-50 text-black text-sm font-semibold rounded-lg transition-colors"
        >
          {screenerMutation.isPending
            ? <RefreshCw size={14} className="animate-spin" />
            : <Clock size={14} />
          }
          {screenerMutation.isPending ? 'Running...' : 'Run Screener'}
        </button>
      </div>

      {/* Goal progress */}
      <div className="card mb-6 border-[#C9A84C33]">
        <div className="flex items-end justify-between mb-4">
          <div>
            <p className="stat-label">Progress to SGD 5,000/month goal</p>
            <p className="text-3xl font-bold text-[#E2C06E] mt-2">
              {fmtSGD(p.monthlyDividend)}
              <span className="text-slate-500 text-base font-normal ml-1">/ month</span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-[#C9A84C]">{fmtPct(progressPct)}</p>
            <p className="text-xs text-slate-500 mt-1">of SGD 5,000 target</p>
          </div>
        </div>
        <div className="w-full bg-[#0B1929] rounded-full h-2.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-[#8B6F2F] via-[#C9A84C] to-[#E2C06E] h-2.5 rounded-full transition-all duration-700"
            style={{ width: `${progressPct}%` }}
          />
        </div>
        <p className="text-xs text-slate-500 mt-2">
          SGD {(TARGET_MONTHLY - p.monthlyDividend).toLocaleString('en-SG', { maximumFractionDigits: 0 })} remaining to goal
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Portfolio Value" value={fmtSGD(p.marketValue)} icon={DollarSign} />
        <StatCard label="Total Invested" value={fmtSGD(p.totalInvested)} icon={TrendingUp} />
        <StatCard
          label="Unrealised P&L"
          value={fmtSGD(p.unrealisedPL)}
          sub={`${p.unrealisedPL >= 0 ? '+' : ''}${fmtPct((p.unrealisedPL / p.totalInvested) * 100)}`}
          icon={p.unrealisedPL >= 0 ? TrendingUp : TrendingDown}
          positive={p.unrealisedPL >= 0}
        />
        <StatCard label="Monthly Dividend" value={fmtSGD(p.monthlyDividend)} icon={PiggyBank} accent />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Annual Dividend" value={fmtSGD(p.annualDividend)} icon={Percent} />
        <StatCard label="Yield on Cost" value={fmtPct(p.yieldOnCost, 2)} sub="based on cost price" icon={Percent} />
        <StatCard label="Holdings" value={`${p.holdingsCount} stocks`} icon={Target} />
        <StatCard
          label="Today's Signals"
          value={signals.length > 0 ? `${signals.filter(s => s.signal === 'BUY_NOW').length} Buy · ${signals.filter(s => s.signal === 'WATCHLIST').length} Watch` : '—'}
          sub={latestDate ?? 'not yet run'}
          icon={Clock}
        />
      </div>

      {/* Holdings table */}
      {p.holdings && p.holdings.length > 0 && (
        <div className="card overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <p className="stat-label">Holdings</p>
            <p className="text-xs text-slate-500">Sorted by market value</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-500 text-xs uppercase tracking-widest border-b border-white/5">
                  <th className="text-left py-2 px-3">Stock</th>
                  <th className="text-right py-2 px-3">Shares</th>
                  <th className="text-right py-2 px-3">Avg Cost</th>
                  <th className="text-right py-2 px-3">Current</th>
                  <th className="text-right py-2 px-3">Market Value</th>
                  <th className="text-right py-2 px-3">P&L</th>
                  <th className="text-right py-2 px-3">Yield</th>
                  <th className="text-right py-2 px-3">Monthly Div</th>
                  <th className="text-right py-2 px-3">YoC</th>
                </tr>
              </thead>
              <tbody>
                {p.holdings.map((h, i) => (
                  <tr
                    key={h.ticker}
                    className={`border-b border-white/5 hover:bg-white/2 transition-colors ${i % 2 === 0 ? '' : 'bg-white/1'}`}
                  >
                    <td className="py-3 px-3">
                      <p className="text-white font-medium text-xs">{h.companyName}</p>
                      <p className="text-slate-500 text-xs font-mono">{h.ticker} · {h.market}</p>
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-slate-300 text-xs">
                      {h.totalShares.toLocaleString('en-SG')}
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-slate-300 text-xs">
                      {h.currency} {h.avgCostPrice.toFixed(3)}
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-xs">
                      <span className={h.currentPrice > h.avgCostPrice ? 'text-green-400' : 'text-red-400'}>
                        {h.currency} {h.currentPrice.toFixed(3)}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-[#E2C06E] text-xs font-semibold">
                      {h.currency} {h.marketValue.toLocaleString('en-SG', { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-3 px-3 text-right text-xs">
                      <span className={h.unrealisedPL >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {h.unrealisedPL >= 0 ? '+' : ''}{h.currency} {h.unrealisedPL.toLocaleString('en-SG', { maximumFractionDigits: 0 })}
                        <br />
                        <span className="text-xs opacity-70">
                          ({h.unrealisedPL >= 0 ? '+' : ''}{h.unrealisedPLPct.toFixed(1)}%)
                        </span>
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-slate-300 text-xs">
                      {h.dividendYield.toFixed(1)}%
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-green-400 text-xs">
                      {h.currency} {h.monthlyDividend.toFixed(0)}
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-[#C9A84C] text-xs">
                      {h.yieldOnCost.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t border-[#C9A84C33] bg-[#0B1929]">
                  <td className="py-3 px-3 text-xs text-slate-400 font-semibold" colSpan={4}>
                    TOTAL
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-[#E2C06E] font-bold text-xs">
                    {fmtSGD(p.marketValue)}
                  </td>
                  <td className="py-3 px-3 text-right text-xs">
                    <span className={p.unrealisedPL >= 0 ? 'text-green-400 font-bold' : 'text-red-400 font-bold'}>
                      {p.unrealisedPL >= 0 ? '+' : ''}{fmtSGD(p.unrealisedPL)}
                    </span>
                  </td>
                  <td className="py-3 px-3"></td>
                  <td className="py-3 px-3 text-right font-mono text-green-400 font-bold text-xs">
                    {fmtSGD(p.monthlyDividend)}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-[#C9A84C] font-bold text-xs">
                    {fmtPct(p.yieldOnCost, 2)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {(!p.holdings || p.holdings.length === 0) && (
        <div className="card text-center py-16">
          <p className="text-slate-400 text-lg mb-2">No holdings yet</p>
          <p className="text-sm text-slate-600 mb-6">
            Add your buy transactions to see your real portfolio here
          </p>
          
            href="/transactions"
            className="px-6 py-2.5 bg-[#C9A84C] hover:bg-[#E2C06E] text-black text-sm font-semibold rounded-lg inline-block"
          >
            Add Transactions
          </a>
        </div>
      )}
    </div>
  )
}