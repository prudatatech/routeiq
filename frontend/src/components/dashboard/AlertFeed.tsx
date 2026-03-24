import { AlertTriangle, RefreshCw, CloudRain, CheckCircle } from 'lucide-react'
import { Card, CardHeader, Badge } from '@/components/ui'

const alerts = [
  {
    id: 1, type: 'warning', icon: AlertTriangle, color: 'var(--accent2)',
    title: 'Traffic jam — NH-48',
    desc: 'V-07 rerouted via Dwarka Exp. +4km, −22min',
    time: '14:28',
  },
  {
    id: 2, type: 'reroute', icon: RefreshCw, color: 'var(--accent3)',
    title: 'VRP re-optimized (47 vehicles)',
    desc: 'AI reduced distance by 12% — saved ₹6,200',
    time: '13:55',
  },
  {
    id: 3, type: 'weather', icon: CloudRain, color: 'var(--warn)',
    title: 'Heavy rain — Gurgaon',
    desc: 'ETA models updated. 6 vehicles rescheduled',
    time: '13:41',
  },
  {
    id: 4, type: 'success', icon: CheckCircle, color: 'var(--accent)',
    title: 'Batch delivery optimized',
    desc: 'Sectors 8–14: 4 trucks → 2 trucks',
    time: '12:10',
  },
]

export default function AlertFeed() {
  return (
    <Card className="border-white/5">
      <CardHeader
        title="AI Events"
        subtitle="Dynamic re-routing & alerts"
        action={<Badge variant="orange">3 ACTIVE</Badge>}
      />
      <div className="px-6 pb-6 space-y-1">
        {alerts.map(({ id, icon: Icon, color, title, desc, time }) => (
          <div key={id} className="flex gap-4 py-4 border-b border-white/5 last:border-0 group hover:bg-white/[0.02] -mx-2 px-2 rounded-xl transition-all">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-inner" style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
              <Icon size={16} style={{ color }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-display font-black text-white text-sm tracking-tight leading-tight mb-1">{title}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wide leading-relaxed">{desc}</div>
            </div>
            <div className="text-[10px] font-black text-slate-600 mono whitespace-nowrap pt-1 uppercase tracking-tighter">{time}</div>
          </div>
        ))}
      </div>
    </Card>
  )
}
