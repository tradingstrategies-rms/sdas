export type SignalType = 'BUY_NOW' | 'WATCHLIST' | 'OVERVALUED'
export type Category = 'Bank' | 'REIT' | 'Infrastructure' | 'Equity'

export interface Signal {
  date: string
  ticker: string
  companyName?: string
  score: number
  signal: SignalType
  amount: number
  yield: number
  notes: string
  category?: Category
}

export interface DailyPrice {
  date: string
  ticker: string
  price: number
  high52: number
  low52: number
  sma50: number
  sma200: number
  rsi14: number
  dividendYield: number
  pbRatio?: number
  peRatio?: number
  drawdownPercent: number
  volume?: number
}

export interface Portfolio {
  totalInvested: number
  marketValue: number
  annualDividend: number
  monthlyDividend: number
  yieldOnCost: number
  cashReserve: number
}

export interface Stock {
  ticker: string
  companyName: string
  sector: string
  category: Category
  targetYield: number
  active: boolean
}

export interface BacktestResult {
  cagr: number
  portfolioValue: number
  totalInvested: number
  annualDividends: number
  monthlyDividends: number
  yieldOnCost: number
  maxDrawdown: number
  dividendReinvestmentValue: number
  portfolioHistory: { date: string; value: number }[]
  trades: object[]
}
