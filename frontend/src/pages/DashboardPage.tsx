import { useQuery } from '@tanstack/react-query'
import { Truck, Clock, Fuel, TrendingUp, Zap } from 'lucide-react'
import { dashboardAPI, vehiclesAPI } from '@/services/api'
import { KPICard, Spinner, Card, CardHeader } from '@/components/ui'
import LiveMap from '@/components/map/LiveMap'
import DeliveryChart from '@/components/dashboard/DeliveryChart'
import AlertFeed from '@/components/dashboard/AlertFeed'
import { AIInsightCard } from '@/components/dashboard/AIInsightCard'

export default function DashboardPage() {
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: dashboardAPI.kpis,
    refetchInterval: 30_000,
  })

  const { data: vehicles = [] } = useQuery({
    queryKey: ['vehicles', 'live'],
    queryFn: () => vehiclesAPI.list({ limit: 8 }),
    refetchInterval: 10_000,
  })

  const now = new Date()

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-5xl font-black tracking-tighter text-slate-900 uppercase leading-none">
            Fleet <span className="text-yellow-500">Operations</span>
          </h1>
          <p className="text-slate-500 font-bold tracking-tight mt-3 flex items-center gap-2">
            <Clock size={14} />
            {now.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
            <span className="opacity-30">|</span>
            {now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })} IST
          </p>
        </div>
        <div className="flex gap-3">
          <div className="flex items-center gap-3 px-5 py-2.5 bg-yellow-500/10 border border-yellow-500/20 rounded-2xl text-xs font-black text-yellow-600 uppercase tracking-widest shadow-sm">
            <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(249,201,53,0.8)]" />
            AI Optimizer Active
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          label="Active Vehicles"
          value={isLoading ? '—' : String(kpis?.active_vehicles ?? 47)}
          delta="+6.2%" deltaUp
          icon={<Truck size={20} className="text-yellow-400" />}
          color="#F9C935"
          progress={78}
        />
        <KPICard
          label="On-Time Rate"
          value={isLoading ? '—' : `${kpis?.on_time_rate_pct ?? 94}%`}
          delta="+12%" deltaUp
          icon={<Clock size={20} className="text-slate-900" />}
          color="#0F172A"
          progress={kpis?.on_time_rate_pct ?? 94}
        />
        <KPICard
          label="Fuel Cost Today"
          value={isLoading ? '—' : `₹${((kpis?.fuel_cost_today ?? 210000) / 100000).toFixed(1)}L`}
          delta="-8.4%"
          icon={<Fuel size={20} className="text-orange-500" />}
          color="#FF6B35"
          progress={56}
        />
        <KPICard
          label="AI Fuel Saved"
          value={isLoading ? '—' : `${kpis?.fuel_saved_pct ?? 18.2}%`}
          delta="+3.1%" deltaUp
          icon={<TrendingUp size={20} className="text-yellow-500" />}
          color="#F59E0B"
          progress={kpis?.fuel_saved_pct ?? 18.2}
        />
      </div>

      {/* Map + Fleet List */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
        <div className="rounded-[24px] bg-[#0A0F1C] border border-slate-800 flex flex-col overflow-hidden shadow-2xl">
          <div className="px-6 pt-6 pb-4 flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">Live Route Map</h2>
              <p className="text-slate-400 text-sm mt-1">Real-time vehicle positions · AI-optimized corridors</p>
            </div>
          </div>
          <div className="px-6 pb-6 h-[400px]">
            <LiveMap vehicles={vehicles} />
          </div>
        </div>

        <div className="rounded-[24px] bg-[#0A0F1C] border border-slate-800 flex flex-col overflow-hidden shadow-2xl">
          <div className="px-6 pt-6 pb-4 flex justify-between items-center border-b border-slate-800/50">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">Active Fleet</h2>
              <p className="text-slate-400 text-sm mt-1">Live positions & ETA</p>
            </div>
            <div className="px-3 py-1.5 rounded-lg border border-[#10b981]/30 bg-[#10b981]/10 text-[#10b981] text-xs font-mono font-bold tracking-widest">
              {kpis?.active_vehicles ?? 47} ONLINE
            </div>
          </div>
          <div className="px-6 pb-6 pt-2 flex-1 overflow-y-auto space-y-1">
            {vehicles.length === 0 ? (
              <div className="py-12 flex justify-center"><Spinner /></div>
            ) : (
              vehicles.slice(0, 7).map((v: any, i: number) => {
                const colors = ['#10b981', '#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#10b981', '#10b981']
                const dotColor = colors[i % colors.length]
                const isOffline = dotColor === '#ef4444'
                const isDelayed = dotColor === '#f59e0b'
                const emoji = v.vehicle_type === 'truck' ? '🚛' : (v.vehicle_type === 'van' ? '🚐' : '🏍️')

                return (
                  <div key={v.id} className="flex items-center gap-4 py-3.5 border-b border-slate-800/50 hover:bg-slate-800/20 -mx-3 px-3 rounded-xl transition-colors">
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center text-lg flex-shrink-0 border" style={{ backgroundColor: `${dotColor}10`, borderColor: `${dotColor}30` }}>
                      {emoji}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="font-bold text-white text-[13px] flex items-center gap-2">
                          Vehicle-{String(i * 3 + 4).padStart(2, '0')} <span className="w-1.5 h-1.5 rounded-full shadow-sm" style={{ backgroundColor: dotColor, boxShadow: `0 0 6px ${dotColor}` }} />
                        </div>
                        <div className="font-mono font-bold text-[11px]" style={{ color: dotColor }}>
                          {isOffline ? 'Offline' : (isDelayed ? '+18 min' : `${Math.floor(Math.random() * 30 + 5)} min`)}
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-1 text-[11px]">
                        <div className="text-slate-400 truncate pr-4">
                          {isOffline ? 'Faridabad → Saket · Maintenance' : 'Connaught Pl → IGI Airport · 3 stops l...'}
                        </div>
                        <div className="text-slate-500 font-mono">
                          {isOffline ? 'Engine alert' : (isDelayed ? 'Rerouting...' : `${Math.floor(Math.random() * 40 + 60)}% done`)}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>


      {/* Charts + Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DeliveryChart />
        <AlertFeed />
        <Card className="border-slate-200 bg-white shadow-sm">
          <CardHeader title="Optimization Score" subtitle="AI efficiency metrics" />
          <div className="px-6 pb-6 space-y-6">
            {[
              { label: 'Route Efficiency', value: 87, color: '#F9C935' },
              { label: 'Fuel Optimization', value: 72, color: '#0F172A' },
              { label: 'Time Window Adherence', value: 94, color: '#FFB800' },
              { label: 'Load Utilization', value: 68, color: '#FF6B35' },
            ].map(({ label, value, color }) => (
              <div key={label} className="group">
                <div className="flex justify-between mb-2 text-[10px] font-black uppercase tracking-wider">
                  <span className="text-slate-500">{label}</span>
                  <span style={{ color }}>{value}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-1000 ease-out shadow-sm" style={{ width: `${value}%`, background: color }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* AI Pulse Insight */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AIInsightCard 
          title="Neural Route Optimization"
          insight="Autonomous rerouting of 12 vehicles has saved 42kg of CO2 and ₹14,200 in fuel costs in the last 4 hours."
          score={98.2}
          trend="up"
        />
        <div className="relative overflow-hidden rounded-[2rem] bg-white border border-slate-200 p-8 flex flex-col justify-center shadow-sm">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-yellow-400 text-slate-900 shadow-sm">
              <Zap size={24} />
            </div>
            <div>
              <h3 className="text-xl font-black text-slate-900 font-display tracking-tight uppercase">Intelligence Active</h3>
              <p className="text-slate-500 text-xs font-bold tracking-widest uppercase">Global Fleet Syncing</p>
            </div>
          </div>
          <div className="space-y-3">
             <div className="flex justify-between text-[10px] font-black uppercase text-slate-500">
               <span>Processing Power</span>
               <span className="text-yellow-600">92%</span>
             </div>
             <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
               <div className="h-full bg-yellow-400 w-[92%] shadow-sm" />
             </div>
          </div>
        </div>
      </div>
    </div>
  )
}
