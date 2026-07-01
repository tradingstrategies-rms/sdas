import { Signal, SignalType } from '@/types'
import { signalBadgeClass, signalEmoji, scoreColor, fmtSGD } from '@/lib/utils'

interface SignalCardProps {
  signal: Signal
  showAmount?: boolean
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round((score / 19) * 100)
  return (
    <div className="flex items-center gap-2 mt-3">
      <div className="flex-1 bg-[#0B1929] rounded-full h-1.5 overflow-hidden">
        <div
          className="h-1.5 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: scoreColor(score) }}
        />
      </div>
      <span className="text-xs font-mono text-slate-400 shrink-0">{score}/19</span>
    </div>
  )
}

export function SignalCard({ signal, showAmount = true }: SignalCardProps) {
  const badgeClass = signalBadgeClass(signal.signal)
  const emoji = signalEmoji(signal.signal)

  return (
    <div className="card hover:border-[#C9A84C44] transition-colors group">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="min-w-0 mr-2">
          <p className="font-semibold text-white truncate">
            {signal.companyName ?? signal.ticker}
          </p>
          <p className="text-xs text-slate-500 font-mono mt-0.5">{signal.ticker}</p>
        </div>
        <span className={badgeClass}>{emoji} {signal.signal.replace('_', ' ')}</span>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="stat-label text-[10px]">Yield</p>
          <p className="text-base font-bold text-[#E2C06E]">{signal.yield.toFixed(1)}%</p>
        </div>
        <div>
          <p className="stat-label text-[10px]">Score</p>
          <p className="text-base font-bold" style={{ color: scoreColor(signal.score) }}>
            {signal.score}
          </p>
        </div>
        {showAmount && (
          <div>
            <p className="stat-label text-[10px]">Deploy</p>
            <p className="text-base font-bold text-white">
              {signal.amount > 0 ? `$${signal.amount}` : '—'}
            </p>
          </div>
        )}
      </div>

      <ScoreBar score={signal.score} />

      {/* Notes */}
      {signal.notes && (
        <p className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-white/5 leading-relaxed">
          {signal.notes}
        </p>
      )}
    </div>
  )
}
