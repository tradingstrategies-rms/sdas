/**
 * Centralised React Query hooks — import these in pages instead of
 * calling useQuery directly, so query keys stay consistent.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { signalsApi, portfolioApi, stocksApi, screenerApi, backtestApi } from '@/lib/api'
import { BacktestResult, Portfolio, Signal, Stock } from '@/types'
import toast from 'react-hot-toast'

// ── Signals ────────────────────────────────────────────────────────────────────

export function useLatestSignals() {
  return useQuery<Signal[]>({
    queryKey: ['signals', 'latest'],
    queryFn: signalsApi.latest,
    staleTime: 5 * 60_000,
  })
}

export function useSignalsByDate(date: string) {
  return useQuery<Signal[]>({
    queryKey: ['signals', 'date', date],
    queryFn: () => signalsApi.byDate(date),
    enabled: !!date,
  })
}

export function useSignalHistory(ticker: string) {
  return useQuery<Signal[]>({
    queryKey: ['signals', 'history', ticker],
    queryFn: () => signalsApi.history(ticker),
    enabled: !!ticker,
  })
}

// ── Portfolio ──────────────────────────────────────────────────────────────────

export function usePortfolio() {
  return useQuery<Portfolio>({
    queryKey: ['portfolio'],
    queryFn: portfolioApi.get,
    staleTime: 2 * 60_000,
  })
}

// ── Stocks ─────────────────────────────────────────────────────────────────────

export function useStocks() {
  return useQuery<Stock[]>({
    queryKey: ['stocks'],
    queryFn: stocksApi.list,
    staleTime: 10 * 60_000,
  })
}

export function useRemoveStock() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (ticker: string) => stocksApi.remove(ticker),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['stocks'] })
      toast.success('Stock removed from watchlist')
    },
    onError: () => toast.error('Failed to remove stock'),
  })
}

export function useAddStock() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (stock: Partial<Stock>) => stocksApi.add(stock),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['stocks'] })
      toast.success('Stock added to watchlist')
    },
    onError: () => toast.error('Failed to add stock'),
  })
}

// ── Screener ───────────────────────────────────────────────────────────────────

export function useRunScreener() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sendEmail = true) => screenerApi.run(sendEmail),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['signals'] })
      toast.success(
        `Screener complete: ${data.buyNow} Buy · ${data.watchlist} Watch · ${data.overvalued} Over`
      )
    },
    onError: () => toast.error('Screener run failed — check backend'),
  })
}

// ── Backtest ───────────────────────────────────────────────────────────────────

export function useRunBacktest() {
  return useMutation<BacktestResult, Error, object>({
    mutationFn: (params) => backtestApi.run(params),
    onError: (err) => toast.error('Backtest failed: ' + err.message),
  })
}
