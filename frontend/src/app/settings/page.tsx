'use client'

import { useState } from 'react'
import { stocksApi } from '@/lib/api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Stock } from '@/types'
import toast from 'react-hot-toast'
import { Trash2, Plus, ChevronDown, ChevronUp } from 'lucide-react'

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

function Section({ title, children, defaultOpen = true }: {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="card mb-4">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between text-left"
      >
        <h2 className="text-sm font-semibold text-[#C9A84C] uppercase tracking-widest">
          {title}
        </h2>
        {open
          ? <ChevronUp size={16} className="text-slate-500" />
          : <ChevronDown size={16} className="text-slate-500" />
        }
      </button>
      {open && <div className="mt-4">{children}</div>}
    </div>
  )
}

function RuleRow({ label, value, highlight = false }: {
  label: string; value: string; highlight?: boolean
}) {
  return (
    <div className={`flex justify-between items-center py-2 border-b border-white/5 text-sm ${highlight ? 'text-[#E2C06E]' : ''}`}>
      <span className="text-slate-400">{label}</span>
      <span className={`font-mono font-semibold ${highlight ? 'text-[#E2C06E]' : 'text-white'}`}>{value}</span>
    </div>
  )
}

function ScoreBlock({ title, rows, maxScore, color = '#C9A84C' }: {
  title: string
  rows: { condition: string; points: string }[]
  maxScore: number
  color?: string
}) {
  return (
    <div className="bg-[#0B1929] rounded-lg p-4 border border-white/5">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-semibold text-white">{title}</p>
        <span className="text-xs px-2 py-0.5 rounded-full border"
          style={{ color, borderColor: color + '44', background: color + '11' }}>
          max +{maxScore}
        </span>
      </div>
      <div className="space-y-1.5">
        {rows.map((row, i) => (
          <div key={i} className="flex justify-between items-center text-xs">
            <span className="text-slate-400">{row.condition}</span>
            <span className="font-mono font-bold text-green-400">{row.points}</span>
          </div>
        ))}
      </div>
    </div>
  )
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
    toast.success('Seed stocks added!')
  }

  return (
    <div className="p-8 max-w-5xl">
      <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
      <p className="text-slate-400 text-sm mb-8">Manage your watchlist and view all scoring rules.</p>

      {/* ── Watchlist ──────────────────────────────────────────────── */}
      <Section title="Watchlist Stocks">
        <div className="flex justify-end mb-4">
          <button
            onClick={handleSeedStocks}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-[#C9A84C22] hover:bg-[#C9A84C33] text-[#C9A84C] rounded-lg transition-colors border border-[#C9A84C33]"
          >
            <Plus size={12} /> Seed 14 Default Stocks
          </button>
        </div>
        {stocks.length === 0 ? (
          <p className="text-slate-500 text-sm py-4 text-center">No stocks yet. Click Seed above to get started.</p>
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
                  <td className="py-2.5 text-slate-400">{s.category}</td>
                  <td className="py-2.5 text-slate-300">{s.targetYield}%</td>
                  <td className="py-2.5 text-right">
                    <button onClick={() => removeMutation.mutate(s.ticker)}
                      className="text-red-500/50 hover:text-red-400 transition-colors">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* ── Signal Thresholds ──────────────────────────────────────── */}
      <Section title="Signal Thresholds">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-900/20 border border-green-800/40 rounded-xl p-4">
            <p className="text-green-400 font-bold text-sm mb-3">🟢 BUY NOW</p>
            <RuleRow label="Min score" value="13 / 19" />
            <RuleRow label="Min yield" value="≥ 4%" />
            <RuleRow label="Price vs SMA200" value="Above" />
            <RuleRow label="Deploy amount" value="SGD 750" highlight />
          </div>
          <div className="bg-amber-900/20 border border-amber-800/40 rounded-xl p-4">
            <p className="text-amber-400 font-bold text-sm mb-3">🟡 WATCHLIST</p>
            <RuleRow label="Min score" value="9 – 12" />
            <RuleRow label="Min yield" value="≥ 4%" />
            <RuleRow label="Price vs SMA200" value="Above" />
            <RuleRow label="Deploy amount" value="SGD 500" highlight />
          </div>
          <div className="bg-red-900/20 border border-red-800/40 rounded-xl p-4">
            <p className="text-red-400 font-bold text-sm mb-3">🔴 OVERVALUED</p>
            <RuleRow label="Score" value="< 9" />
            <RuleRow label="OR yield" value="< 4%" />
            <RuleRow label="OR price" value="Below SMA200" />
            <RuleRow label="Deploy amount" value="SGD 0" />
          </div>
        </div>
      </Section>

      {/* ── Scoring Rules ──────────────────────────────────────────── */}
      <Section title="Scoring Rules — Max 19 Points">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">

          <ScoreBlock
            title="📈 Trend Score"
            maxScore={4}
            color="#6366f1"
            rows={[
              { condition: "Price > SMA200", points: "+2" },
              { condition: "Price > SMA50", points: "+1" },
              { condition: "SMA50 > SMA200 (golden cross)", points: "+1" },
            ]}
          />

          <ScoreBlock
            title="📉 Pullback Score"
            maxScore={3}
            color="#06b6d4"
            rows={[
              { condition: "Drawdown < 5% from 52w high", points: "+0" },
              { condition: "Drawdown 5% – 10%", points: "+1" },
              { condition: "Drawdown 10% – 15%", points: "+2" },
              { condition: "Drawdown > 15%", points: "+3" },
            ]}
          />

          <ScoreBlock
            title="💰 Dividend Score — Banks"
            maxScore={2}
            color="#C9A84C"
            rows={[
              { condition: "Yield > 4.5%", points: "+1" },
              { condition: "Yield > 5.0%", points: "+2" },
            ]}
          />

          <ScoreBlock
            title="💰 Dividend Score — REITs"
            maxScore={3}
            color="#C9A84C"
            rows={[
              { condition: "Yield > 5.5%", points: "+1" },
              { condition: "Yield > 6.5%", points: "+2" },
              { condition: "Yield > 7.5%", points: "+3" },
            ]}
          />

          <ScoreBlock
            title="💰 Dividend Score — Infrastructure"
            maxScore={2}
            color="#C9A84C"
            rows={[
              { condition: "Yield > 6.5%", points: "+2" },
            ]}
          />

          <ScoreBlock
            title="💰 Dividend Score — Equities"
            maxScore={1}
            color="#C9A84C"
            rows={[
              { condition: "Yield > 4.0%", points: "+1" },
            ]}
          />

          <ScoreBlock
            title="📊 Valuation Score (PB Ratio)"
            maxScore={2}
            color="#8b5cf6"
            rows={[
              { condition: "PB below 5-year average", points: "+1" },
              { condition: "PB 10%+ below average", points: "+2" },
            ]}
          />

          <ScoreBlock
            title="🔻 RSI Score"
            maxScore={3}
            color="#ec4899"
            rows={[
              { condition: "RSI < 50", points: "+1" },
              { condition: "RSI < 40", points: "+2" },
              { condition: "RSI < 30 (oversold)", points: "+3" },
            ]}
          />

          <ScoreBlock
            title="🌏 Market Correction Bonus (STI)"
            maxScore={4}
            color="#10b981"
            rows={[
              { condition: "STI down > 5% from 52w high", points: "+1" },
              { condition: "STI down > 10%", points: "+2" },
              { condition: "STI down > 20%", points: "+4" },
            ]}
          />

        </div>
      </Section>

      {/* ── Master Rules ───────────────────────────────────────────── */}
      <Section title="Master Rules">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="bg-[#0B1929] rounded-lg p-4 border border-red-900/30">
              <p className="text-red-400 text-xs font-semibold uppercase tracking-widest mb-2">Rule 1 — Never buy below min yield</p>
              <p className="text-slate-300 text-sm">If dividend yield &lt; 4%, immediately classify as <span className="text-red-400 font-bold">OVERVALUED</span>. No exceptions.</p>
            </div>
            <div className="bg-[#0B1929] rounded-lg p-4 border border-red-900/30">
              <p className="text-red-400 text-xs font-semibold uppercase tracking-widest mb-2">Rule 2 — Never buy below SMA200</p>
              <p className="text-slate-300 text-sm">If price &lt; SMA200, stock is in a downtrend. Immediately classify as <span className="text-red-400 font-bold">OVERVALUED</span>.</p>
            </div>
            <div className="bg-[#0B1929] rounded-lg p-4 border border-amber-900/30">
              <p className="text-amber-400 text-xs font-semibold uppercase tracking-widest mb-2">Rule 3 — Max position size</p>
              <p className="text-slate-300 text-sm">No single stock can exceed <span className="text-amber-400 font-bold">15%</span> of total portfolio value.</p>
            </div>
          </div>
          <div className="space-y-3">
            <div className="bg-[#0B1929] rounded-lg p-4 border border-amber-900/30">
              <p className="text-amber-400 text-xs font-semibold uppercase tracking-widest mb-2">Rule 4 — Cash reserve</p>
              <p className="text-slate-300 text-sm">Always maintain <span className="text-amber-400 font-bold">20%</span> cash reserve. Never be fully invested.</p>
            </div>
            <div className="bg-[#0B1929] rounded-lg p-4 border border-green-900/30">
              <p className="text-green-400 text-xs font-semibold uppercase tracking-widest mb-2">Rule 5 — Reinvest dividends</p>
              <p className="text-slate-300 text-sm">All dividends received are automatically reinvested to compound growth.</p>
            </div>
            <div className="bg-[#0B1929] rounded-lg p-4 border border-green-900/30">
              <p className="text-green-400 text-xs font-semibold uppercase tracking-widest mb-2">Rule 6 — Deploy cash in crashes</p>
              <div className="space-y-1 text-sm text-slate-300 mt-1">
                <p>STI down &gt; 10% → invest extra <span className="text-green-400 font-bold">SGD 1,000</span></p>
                <p>STI down &gt; 20% → deploy <span className="text-green-400 font-bold">50%</span> cash reserve</p>
                <p>STI down &gt; 30% → deploy <span className="text-green-400 font-bold">100%</span> cash reserve</p>
              </div>
            </div>
          </div>
        </div>
      </Section>

      {/* ── Investment Amounts ─────────────────────────────────────── */}
      <Section title="Investment Amounts" defaultOpen={false}>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <RuleRow label="BUY NOW per stock" value="SGD 750" highlight />
            <RuleRow label="WATCHLIST per stock" value="SGD 500" />
            <RuleRow label="Max position size" value="15% of portfolio" />
            <RuleRow label="Min cash reserve" value="20% of portfolio" />
          </div>
          <div>
            <RuleRow label="STI crash > 10%" value="+ SGD 1,000" highlight />
            <RuleRow label="STI crash > 20%" value="50% of cash reserve" highlight />
            <RuleRow label="STI crash > 30%" value="100% of cash reserve" highlight />
          </div>
        </div>
      </Section>

    </div>
  )
}