'use client'

import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { scoreColor } from '@/lib/utils'

interface ScoreBreakdown {
  trend: number
  pullback: number
  dividend: number
  valuation: number
  rsi: number
  market_correction: number
}

interface ScoreBreakdownChartProps {
  breakdown: ScoreBreakdown
  total: number
}

const MAX_SCORES: Record<string, number> = {
  Trend: 4,
  Pullback: 3,
  Dividend: 3,
  Valuation: 2,
  RSI: 3,
  'Mkt Corr.': 4,
}

export function ScoreBreakdownChart({ breakdown, total }: ScoreBreakdownChartProps) {
  const data = [
    { name: 'Trend', score: breakdown.trend, max: MAX_SCORES['Trend'] },
    { name: 'Pullback', score: breakdown.pullback, max: MAX_SCORES['Pullback'] },
    { name: 'Dividend', score: breakdown.dividend, max: MAX_SCORES['Dividend'] },
    { name: 'Valuation', score: breakdown.valuation, max: MAX_SCORES['Valuation'] },
    { name: 'RSI', score: breakdown.rsi, max: MAX_SCORES['RSI'] },
    { name: 'Mkt Corr.', score: breakdown.market_correction, max: MAX_SCORES['Mkt Corr.'] },
  ]

  const color = scoreColor(total)

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="stat-label">Score Breakdown</p>
        <p className="text-xl font-bold font-mono" style={{ color }}>
          {total} / 19
        </p>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
          <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} />
          <YAxis hide domain={[0, 4]} />
          <Tooltip
            contentStyle={{ background: '#132337', border: '1px solid #C9A84C33', borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: '#C9A84C' }}
            itemStyle={{ color: '#fff' }}        
			formatter={(v, _name, item) => {
				const max = (item.payload as { max?: number })?.max;
				return [`${v}${max !== undefined ? ` / ${max}` : ''}`, 'Score'];
			}}
          />
          <Bar dataKey="score" radius={[3, 3, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.score === 0 ? '#1e2d3d' : color}
                fillOpacity={entry.score === 0 ? 1 : 0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
