import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Zap, Play, CheckCircle } from 'lucide-react'
import { optimizationAPI } from '@/services/api'
import { Card, CardHeader, Badge, Button } from '@/components/ui'
import toast from 'react-hot-toast'

export default function OptimizePage() {
  const [algo, setAlgo] = useState('ortools')
  const [traffic, setTraffic] = useState(true)
  const [weather, setWeather] = useState(true)
  const [solveTime, setSolveTime] = useState(30)

  const { mutate: runOptimization, data: result, isPending } = useMutation({
    mutationFn: () => optimizationAPI.optimize({
      depot_id: '00000000-0000-0000-0000-000000000001',
      vehicle_ids: [],
      delivery_point_ids: [],
      algorithm: algo,
      consider_traffic: traffic,
      consider_weather: weather,
      max_solve_time_seconds: solveTime,
    }),
    onSuccess: (data) => toast.success(`Optimized ${data.routes?.length ?? 0} routes in ${data.solve_time_seconds?.toFixed(2)}s`),
    onError: () => {},
  })

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 800, letterSpacing: '-0.5px', color: '#0F172A' }}>
          Route Optimizer
        </h1>
        <p style={{ color: '#64748B', fontSize: 13, marginTop: 2 }}>
          AI-powered VRP solver with real-time traffic & weather integration
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: 20 }}>
        {/* Config Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card>
            <CardHeader title="Solver Configuration" />
            <div style={{ padding: '0 20px 20px' }}>
              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 12, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.6px', display: 'block', marginBottom: 10 }}>
                  Algorithm
                </label>
                {[
                  { value: 'ortools', label: 'Google OR-Tools', desc: 'Constraint programming · Most accurate' },
                  { value: 'genetic', label: 'Genetic Algorithm', desc: 'Evolutionary · Good for large fleets' },
                  { value: 'reinforcement', label: 'Reinforcement Learning', desc: 'Deep RL · Learns from history' },
                ].map(opt => (
                  <div
                    key={opt.value}
                    onClick={() => setAlgo(opt.value)}
                    style={{
                      padding: '12px 14px', borderRadius: 8, marginBottom: 8,
                      border: `1px solid ${algo === opt.value ? 'rgba(234,179,8,0.4)' : '#E2E8F0'}`,
                      background: algo === opt.value ? 'rgba(234,179,8,0.05)' : '#F8FAFC',
                      cursor: 'pointer', transition: 'all 0.15s',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{
                        width: 16, height: 16, borderRadius: '50%',
                        border: `2px solid ${algo === opt.value ? '#EAB308' : '#cbd5e1'}`,
                        background: algo === opt.value ? '#EAB308' : 'transparent',
                        flexShrink: 0,
                      }} />
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A' }}>{opt.label}</div>
                        <div style={{ fontSize: 11, color: '#64748B', marginTop: 1 }}>{opt.desc}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Toggles */}
              {[
                { label: 'Real-time Traffic', value: traffic, set: setTraffic, desc: 'Google Maps / TomTom API' },
                { label: 'Weather Conditions', value: weather, set: setWeather, desc: 'OpenWeather API' },
              ].map(({ label, value, set, desc }) => (
                <div key={label} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '12px 0', borderBottom: '1px solid #E2E8F0',
                }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: '#0F172A' }}>{label}</div>
                    <div style={{ fontSize: 11, color: '#64748B' }}>{desc}</div>
                  </div>
                  <div
                    onClick={() => set(!value)}
                    style={{
                      width: 44, height: 24, borderRadius: 12, cursor: 'pointer',
                      background: value ? '#EAB308' : '#cbd5e1',
                      position: 'relative', transition: 'background 0.2s',
                    }}
                  >
                    <div style={{
                      position: 'absolute', top: 3, left: value ? 23 : 3,
                      width: 18, height: 18, borderRadius: '50%',
                      background: value ? '#050A0E' : '#FFFFFF',
                      transition: 'left 0.2s',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
                    }} />
                  </div>
                </div>
              ))}

              {/* Max solve time */}
              <div style={{ marginTop: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <label style={{ fontSize: 12, color: '#64748B', fontWeight: 600 }}>Max Solve Time</label>
                  <span style={{ fontFamily: 'monospace', fontSize: 12, color: '#EAB308', fontWeight: 'bold' }}>
                    {solveTime}s
                  </span>
                </div>
                <input
                  type="range" min={5} max={300} value={solveTime}
                  onChange={e => setSolveTime(+e.target.value)}
                  style={{ width: '100%', accentColor: '#EAB308' }}
                />
              </div>

              <Button
                variant="accent"
                onClick={() => runOptimization()}
                disabled={isPending}
              >
                <Play size={14} />
                {isPending ? 'Optimizing...' : 'Run Optimization'}
              </Button>
            </div>
          </Card>
        </div>

        {/* Results */}
        <div>
          <Card>
            <CardHeader
              title="Optimization Results"
              subtitle={result ? `Solved in ${result.solve_time_seconds?.toFixed(2)}s` : 'Configure and run optimization'}
              action={result ? <Badge variant="green">Completed</Badge> : undefined}
            />
            <div style={{ padding: '0 20px 20px' }}>
              {!result ? (
                <div style={{
                  height: 300, display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center', gap: 12,
                  color: '#94a3b8',
                }}>
                  <Zap size={40} style={{ opacity: 0.3 }} />
                  <p style={{ fontSize: 13, fontWeight: 500 }}>Configure solver and click "Run Optimization"</p>
                </div>
              ) : (
                <>
                  {/* Stats */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
                    {[
                      { label: 'Routes', value: result.routes?.length ?? 0 },
                      { label: 'Total Distance', value: `${result.total_distance_km?.toFixed(1)} km` },
                      { label: 'Total Fuel', value: `${result.total_fuel_liters?.toFixed(1)} L` },
                      { label: 'AI Savings', value: `${result.estimated_savings_pct?.toFixed(1)}%` },
                    ].map(({ label, value }) => (
                      <div key={label} style={{
                        background: '#F8FAFC', borderRadius: 10,
                        padding: '14px 16px', border: '1px solid #E2E8F0',
                      }}>
                        <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 800, color: '#EAB308' }}>
                          {value}
                        </div>
                        <div style={{ fontSize: 11, color: '#64748B', marginTop: 4, fontWeight: 600 }}>{label}</div>
                      </div>
                    ))}
                  </div>

                  {/* Route list */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {(result.routes ?? []).slice(0, 5).map((r: any, i: number) => (
                      <div key={r.id ?? i} style={{
                        padding: '12px 16px', borderRadius: 8,
                        background: '#F8FAFC', border: '1px solid #E2E8F0',
                        display: 'flex', alignItems: 'center', gap: 12,
                      }}>
                        <CheckCircle size={16} color="#EAB308" />
                        <div style={{ flex: 1, fontSize: 13, color: '#0F172A', fontWeight: 500 }}>
                          Route {i + 1} — Vehicle {r.vehicle_id?.slice(-8)}
                        </div>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <Badge variant="green">{r.total_distance_km?.toFixed(1)} km</Badge>
                          <Badge variant="blue">{r.total_duration_minutes?.toFixed(0)} min</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
