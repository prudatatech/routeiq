import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Truck, X, Fuel, Info, AlertCircle, MapPin, BarChart2, Settings } from 'lucide-react'
import { vehiclesAPI } from '@/services/api'
import { Card, StatusDot, Button, Spinner } from '@/components/ui'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'
import clsx from 'clsx'

const STATUS_OPTIONS = ['all', 'on_route', 'available', 'idle', 'maintenance', 'offline']
const VEHICLE_TYPES = ['truck', 'van', 'bike', 'car']
const FUEL_TYPES = ['diesel', 'petrol', 'electric', 'cng']

function AddVehicleModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    plate_number: '',
    vehicle_type: 'truck',
    capacity_kg: 1000,
    fuel_type: 'diesel',
    fuel_capacity_liters: 60,
    fuel_efficiency_kmpl: 12,
  })

  const mutation = useMutation({
    mutationFn: (data: typeof formData) => vehiclesAPI.create({ ...data, status: 'available' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      queryClient.invalidateQueries({ queryKey: ['fleet-summary'] })
      toast.success('Vehicle added successfully')
      onClose()
      setFormData({
        plate_number: '',
        vehicle_type: 'truck',
        capacity_kg: 1000,
        fuel_type: 'diesel',
        fuel_capacity_liters: 60,
        fuel_efficiency_kmpl: 12,
      })
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to add vehicle')
    }
  })

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={onClose} />
      <Card className="w-full max-w-md animate-fade-up relative z-10 glass shadow-xl overflow-hidden border-slate-200 bg-white" glass={false}>
        <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-yellow-400/20 rounded-lg flex items-center justify-center border border-yellow-400/30">
              <Truck size={16} className="text-yellow-400" />
            </div>
            <h2 className="font-heading font-bold text-lg text-slate-900">Add New Vehicle</h2>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-900 transition-colors">
            <X size={20} />
          </button>
        </div>

        <form className="p-6 space-y-4" onSubmit={(e) => { e.preventDefault(); mutation.mutate(formData); }}>
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase tracking-widest font-bold text-slate-500 ml-1">Plate Number</label>
            <input
              required
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-yellow-400/50 transition-colors mono"
              placeholder="e.g. DL-1005"
              value={formData.plate_number}
              onChange={e => setFormData({ ...formData, plate_number: e.target.value.toUpperCase() })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase tracking-widest font-bold text-slate-500 ml-1">Vehicle Type</label>
              <select
                className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-yellow-400/50 transition-colors"
                value={formData.vehicle_type}
                onChange={e => setFormData({ ...formData, vehicle_type: e.target.value })}
              >
                {VEHICLE_TYPES.map(t => <option key={t} value={t} className="bg-white">{t.toUpperCase()}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase tracking-widest font-bold text-slate-500 ml-1">Capacity (kg)</label>
              <input
                type="number"
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-yellow-400/50 transition-colors mono"
                value={formData.capacity_kg}
                onChange={e => setFormData({ ...formData, capacity_kg: Number(e.target.value) })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase tracking-widest font-bold text-slate-500 ml-1">Fuel Type</label>
              <select
                className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-yellow-400/50 transition-colors"
                value={formData.fuel_type}
                onChange={e => setFormData({ ...formData, fuel_type: e.target.value })}
              >
                {FUEL_TYPES.map(t => <option key={t} value={t} className="bg-white">{t.toUpperCase()}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase tracking-widest font-bold text-slate-500 ml-1">Efficiency (km/L)</label>
              <input
                type="number"
                step="0.1"
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-yellow-400/50 transition-colors mono"
                value={formData.fuel_efficiency_kmpl}
                onChange={e => setFormData({ ...formData, fuel_efficiency_kmpl: Number(e.target.value) })}
              />
            </div>
          </div>

          <div className="pt-4 flex gap-3">
            <Button variant="ghost" className="flex-1" onClick={onClose} type="button">Cancel</Button>
            <Button variant="accent" className="flex-1" type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? <Spinner size={16} /> : 'Save Vehicle'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}

export default function FleetPage() {
  const role = useAuthStore(s => s.role)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)

  const { data: vehicles = [], isLoading } = useQuery({
    queryKey: ['vehicles', filter],
    queryFn: () => vehiclesAPI.list({ status: filter === 'all' ? undefined : filter, limit: 100 }),
    refetchInterval: 15_000,
  })

  const { data: summary } = useQuery({
    queryKey: ['fleet-summary'],
    queryFn: vehiclesAPI.summary,
  })

  const filtered = vehicles.filter((v: any) =>
    v.plate_number.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="font-display text-5xl font-black text-slate-900 tracking-tighter uppercase leading-none">
            Fleet <span className="text-yellow-500">Intelligence</span>
          </h1>
          <p className="text-slate-500 font-bold tracking-tight mt-3 flex items-center gap-2">
            <Info size={14} className="text-yellow-600" />
            Monitoring <span className="text-slate-900">{summary?.total ?? '—'}</span> high-performance assets in real-time
          </p>
        </div>
        {role !== 'driver' && (
          <Button variant="accent" size="md" className="shadow-yellow-400/20" onClick={() => setIsModalOpen(true)}>
            <Plus size={18} strokeWidth={3} /> Add New Asset
          </Button>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total Fleet', value: summary?.total ?? 0, colorClass: 'text-slate-900' },
          { label: 'Live Delivery', value: summary?.active ?? 0, colorClass: 'text-yellow-600' },
          { label: 'Idle Ready', value: summary?.idle ?? 0, colorClass: 'text-slate-400' },
          { label: 'Scheduled Maint.', value: summary?.maintenance ?? 0, colorClass: 'text-orange-500' },
          { label: 'Disconnected', value: summary?.offline ?? 0, colorClass: 'text-red-500' },
        ].map(({ label, value, colorClass }) => (
          <div key={label} className="glass-card p-6 relative group overflow-hidden border-slate-200 bg-white shadow-sm">
            <div className={clsx("font-display text-4xl font-black mb-1 leading-none tracking-tighter", colorClass)}>{value}</div>
            <div className={clsx("text-[10px] font-black uppercase tracking-[0.2em] mt-1", colorClass)}>{label}</div>
            <div className="absolute -right-4 -bottom-4 opacity-[0.03] rotate-12 group-hover:rotate-0 transition-all duration-500 grayscale">
              <Truck size={80} />
            </div>
          </div>
        ))}
      </div>

      {/* Filters + Search */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-4 py-2 w-full max-w-sm focus-within:border-yellow-400/50 transition-colors shadow-sm">
          <Search size={16} className="text-slate-400" />
          <input
            placeholder="Search assets by plate..."
            className="bg-transparent border-none outline-none text-sm text-slate-900 w-full placeholder:text-slate-400"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
          {STATUS_OPTIONS.map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={clsx(
                "px-4 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all",
                filter === s ? "bg-white text-slate-900 shadow-sm border border-slate-200" : "text-slate-500 hover:text-slate-700"
              )}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Table Section */}
      <Card className="border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Asset Details', 'Telemetry', 'Status', 'Payload', 'Efficiency', 'Location', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-5 text-left text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-20">
                    <div className="flex flex-col items-center justify-center gap-3">
                      <Spinner size={32} />
                      <span className="text-slate-500 text-xs font-heading">Synchronizing Fleet Vector...</span>
                    </div>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-20">
                    <div className="flex flex-col items-center justify-center text-slate-500 gap-2">
                      <AlertCircle size={24} strokeWidth={1.5} />
                      <span className="text-xs">No active assets found matching criteria</span>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map((v: any, idx: number) => (
                  <tr key={v.id} 
                    className="border-b border-slate-100 hover:bg-slate-50 transition-colors group"
                    style={{ animationDelay: (idx * 50) + 'ms' }}
                  >
                    <td className="px-6 py-5">
                      <div className="font-display font-black text-slate-900 text-base group-hover:text-yellow-600 transition-all uppercase tracking-tight">{v.plate_number}</div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="text-[10px] font-black uppercase bg-slate-100 border border-slate-200 px-2 py-1 rounded w-fit text-slate-500 tracking-widest">
                        {v.vehicle_type}
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 w-fit">
                        <StatusDot status={v.status} />
                        <span className="text-[10px] font-black text-slate-900 uppercase tracking-widest">{v.status.replace('_', ' ')}</span>
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="text-xs text-slate-900 font-black tracking-tight">{v.capacity_kg}<span className="text-[10px] text-slate-500 ml-1">KG CAP</span></div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-2">
                        <Fuel size={12} className="text-yellow-500" />
                        <span className="font-display font-black text-xs text-slate-900 pb-0.5">{v.fuel_efficiency_kmpl}</span>
                        <span className="text-[10px] font-black text-slate-500">KM/L</span>
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="font-mono text-[10px] text-slate-500 leading-tight">
                        {v.latitude ? (
                          <div className="flex items-center gap-2">
                            <span className="text-yellow-500">●</span>
                            <span className="text-slate-600">{v.latitude.toFixed(4)}, {v.longitude.toFixed(4)}</span>
                          </div>
                        ) : (
                          <span className="text-red-900 font-black">NO SIGNAL</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => toast.success('Initiating live tracking for ' + v.plate_number + '...')}
                          className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-yellow-600 transition-colors tooltip tooltip-left" data-tip="Live Tracking"
                        >
                          <MapPin size={16} />
                        </button>
                        <button 
                          onClick={() => toast.success('Loading analytics for ' + v.plate_number + '...')}
                          className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-900 transition-colors tooltip tooltip-top" data-tip="Analytics"
                        >
                          <BarChart2 size={16} />
                        </button>
                        <button 
                          onClick={() => toast.success('Opening settings for ' + v.plate_number + '...')}
                          className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-900 transition-colors tooltip tooltip-top" data-tip="Asset Settings"
                        >
                          <Settings size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <AddVehicleModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
