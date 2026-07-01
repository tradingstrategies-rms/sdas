import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { SignalType } from '@/types'

/** Merge Tailwind classes safely. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format a number as SGD currency. */
export function fmtSGD(value: number, decimals = 0): string {
  return `SGD ${value.toLocaleString('en-SG', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`
}

/** Format percentage. */
export function fmtPct(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`
}

/** Return Tailwind badge class for a signal type. */
export function signalBadgeClass(signal: SignalType): string {
  return signal === 'BUY_NOW'
    ? 'badge-buy'
    : signal === 'WATCHLIST'
    ? 'badge-watch'
    : 'badge-over'
}

/** Return emoji for a signal type. */
export function signalEmoji(signal: SignalType): string {
  return signal === 'BUY_NOW' ? '🟢' : signal === 'WATCHLIST' ? '🟡' : '🔴'
}

/** Score colour (green / amber / red). */
export function scoreColor(score: number): string {
  if (score >= 13) return '#16a34a'
  if (score >= 9) return '#d97706'
  return '#dc2626'
}

/** Calculate years to SGD 5,000/month given current monthly dividend + growth rate. */
export function yearsToGoal(
  monthlyDiv: number,
  target = 5000,
  annualGrowthRate = 0.12,
): number | null {
  if (monthlyDiv <= 0) return null
  if (monthlyDiv >= target) return 0
  // FV = PV * (1+r)^n  →  n = ln(FV/PV) / ln(1+r)
  return Math.log(target / monthlyDiv) / Math.log(1 + annualGrowthRate)
}
