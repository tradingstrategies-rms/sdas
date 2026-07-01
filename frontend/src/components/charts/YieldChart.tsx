'use client'

import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

interface YieldChartProps {
  data: { ticker: string; yield: number; signal: string }[]
  minYield?: number
  height?: number
}

const SIGNAL_COLORS: Record<string, string> = {
  BUY_NOW:    '#16a34a',
  WATCHLIST:  '#d97706',
  OVERVALUED: '#ef4444',
}

export function YieldChart({ data, minYield = 4, height = 220 }: YieldChartProps) {
  const sorted = [...data].sort((a, b) => b.yield - a.yield)

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={sorted} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
        <XAxis
          dataKey="ticker"
          tick={{ fill: '#64748b', fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: string) => v.replace('.SI', '')}
        />
        <YAxis
          tick={{ fill: '#64748b', fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: number) => `${v}%`}
          domain={[0, 'auto']}
        />
        <Tooltip
          contentStyle={{ background: '#132337', border: '1px solid #C9A84C33', borderRadius: 6, fontSize: 12 }}
          labelStyle={{ color: '#C9A84C' }}
          itemStyle={{ color: '#fff' }}
          formatter={(v: number) => [`${v.toFixed(1)}%`, 'Dividend Yield']}
        />
        <ReferenceLine
          y={minYield}
          stroke="#C9A84C"
          strokeDasharray="4 4"
          strokeOpacity={0.6}
          label={{ value: `${minYield}% min`, fill: '#C9A84C88', fontSize: 10, position: 'insideTopRight' }}
        />
        <Bar dataKey="yield" radius={[3, 3, 0, 0]}>
          {sorted.map((entry, i) => (
            <Cell key={i} fill={SIGNAL_COLORS[entry.signal] ?? '#475569'} fillOpacity={0.8} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
