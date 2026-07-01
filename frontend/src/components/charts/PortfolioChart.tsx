'use client'

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'

interface PortfolioChartProps {
  data: { date: string; value: number }[]
  targetValue?: number
  height?: number
}

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean
  payload?: { value: number }[]
  label?: string
}) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#132337] border border-[#C9A84C33] rounded-lg p-3 text-sm shadow-xl">
      <p className="text-[#C9A84C] font-medium mb-1">{label}</p>
      <p className="text-white font-bold">
        SGD {payload[0].value.toLocaleString('en-SG', { maximumFractionDigits: 0 })}
      </p>
    </div>
  )
}

export function PortfolioChart({ data, targetValue, height = 280 }: PortfolioChartProps) {
  if (!data?.length) {
    return (
      <div className="flex items-center justify-center text-slate-500 text-sm" style={{ height }}>
        No chart data available yet.
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#C9A84C" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#C9A84C" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff06" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fill: '#475569', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: string) => v.slice(0, 7)}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fill: '#475569', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: number) =>
            v >= 1000 ? `$${(v / 1000).toFixed(0)}k` : `$${v}`
          }
          width={52}
        />
        <Tooltip content={<CustomTooltip />} />
        {targetValue && (
          <ReferenceLine
            y={targetValue}
            stroke="#C9A84C"
            strokeDasharray="4 4"
            strokeOpacity={0.5}
            label={{ value: 'Target', fill: '#C9A84C', fontSize: 11, position: 'insideTopRight' }}
          />
        )}
        <Area
          type="monotone"
          dataKey="value"
          stroke="#C9A84C"
          strokeWidth={2}
          fill="url(#portfolioGradient)"
          dot={false}
          activeDot={{ r: 4, fill: '#C9A84C', stroke: '#0B1929', strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
