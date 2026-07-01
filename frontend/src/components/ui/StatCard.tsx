import { cn } from '@/lib/utils'

interface StatCardProps {
  label: string
  value: string
  sub?: string
  icon?: React.ElementType
  accent?: boolean
  trend?: 'up' | 'down' | 'neutral'
  className?: string
}

export function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  accent = false,
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        'card',
        accent && 'border-[#C9A84C55] bg-gradient-to-br from-[#132337] to-[#1a2e45]',
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="stat-label truncate">{label}</p>
          <p className={cn('stat-value mt-1 truncate', accent && 'text-[#E2C06E]')}>
            {value}
          </p>
          {sub && <p className="text-xs text-slate-500 mt-1 truncate">{sub}</p>}
        </div>
        {Icon && (
          <div className={cn('p-2 rounded-lg shrink-0 ml-3', accent ? 'bg-[#C9A84C22]' : 'bg-white/5')}>
            <Icon size={18} className={accent ? 'text-[#C9A84C]' : 'text-slate-400'} />
          </div>
        )}
      </div>
    </div>
  )
}
