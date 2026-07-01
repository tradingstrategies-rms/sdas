'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, TrendingUp, ListChecks, CalendarDays,
  BarChart3, Receipt, Settings, Zap,
} from 'lucide-react'

const NAV = [
  { href: '/dashboard', label: 'Portfolio', icon: LayoutDashboard },
  { href: '/signals', label: 'Signals', icon: Zap },
  { href: '/watchlist', label: 'Watchlist', icon: ListChecks },
  { href: '/dividends', label: 'Dividends', icon: CalendarDays },
  { href: '/performance', label: 'Performance', icon: TrendingUp },
  { href: '/backtest', label: 'Backtest', icon: BarChart3 },
  { href: '/transactions', label: 'Transactions', icon: Receipt },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const path = usePathname()

  return (
    <aside className="w-56 min-h-screen bg-[#0a1520] border-r border-[#C9A84C1A] flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-5 py-6 border-b border-[#C9A84C1A]">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#C9A84C] to-[#8B6F2F] flex items-center justify-center text-sm font-bold text-black">
            S
          </div>
          <div>
            <p className="text-xs font-bold text-[#C9A84C] tracking-widest uppercase">SDAS</p>
            <p className="text-[10px] text-slate-500 leading-tight">SGX Dividend Screener</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = path.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group
                ${active
                  ? 'bg-[#C9A84C15] text-[#C9A84C] border border-[#C9A84C33]'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
            >
              <Icon size={16} className={active ? 'text-[#C9A84C]' : 'text-slate-500 group-hover:text-slate-300'} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Goal indicator */}
      <div className="px-4 py-4 border-t border-[#C9A84C1A]">
        <p className="text-[10px] text-slate-500 mb-1 uppercase tracking-widest">Monthly Target</p>
        <p className="text-[#C9A84C] font-bold text-lg">SGD 5,000</p>
        <p className="text-[10px] text-slate-600">passive income goal</p>
      </div>
    </aside>
  )
}
