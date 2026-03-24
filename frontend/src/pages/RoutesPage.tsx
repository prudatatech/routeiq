import { useQuery } from '@tanstack/react-query'
import { routesAPI } from '@/services/api'
import { Card, Badge, StatusDot } from '@/components/ui'
import { format } from 'date-fns'

export default function RoutesPage() {
  const { data: routes = [], isLoading } = useQuery({
    queryKey: ['routes'],
    queryFn: () => routesAPI.list({ limit: 50 }),
    refetchInterval: 20_000,
  })

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 800, letterSpacing: '-0.5px', color: '#0F172A' }}>
          Routes
        </h1>
        <p style={{ color: '#64748B', fontSize: 13, marginTop: 2 }}>
          All active and completed routes
        </p>
      </div>

      <Card>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #E2E8F0', backgroundColor: '#F8FAFC' }}>
              {['Route ID', 'Vehicle', 'Status', 'Distance', 'Duration', 'Fuel Est.', 'Score', 'Created'].map(h => (
                <th key={h} style={{
                  padding: '12px 16px', textAlign: 'left',
                  fontSize: 11, color: '#64748B',
                  textTransform: 'uppercase', letterSpacing: '0.6px', fontWeight: 600,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: '#64748B' }}>Loading routes...</td></tr>
            ) : routes.length === 0 ? (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: '#64748B' }}>
                No routes yet. Run the optimizer to create routes.
              </td></tr>
            ) : routes.map((r: any) => (
              <tr key={r.id}
                style={{ borderBottom: '1px solid #E2E8F0', cursor: 'pointer', transition: 'background 0.2s' }}
                onMouseEnter={e => (e.currentTarget.style.background = '#F8FAFC')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
              >
                <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: 12, color: '#0F172A', fontWeight: 500 }}>
                  {r.id.slice(0, 8)}...
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: 12, color: '#0F172A', fontWeight: 500 }}>
                  {r.vehicle_id.slice(0, 8)}...
                </td>
                <td style={{ padding: '12px 16px', color: '#0F172A', fontWeight: 500 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <StatusDot status={r.status === 'active' ? 'on_route' : r.status === 'completed' ? 'available' : 'idle'} />
                    <span style={{ fontSize: 12 }}>{r.status}</span>
                  </div>
                </td>
                <td style={{ padding: '12px 16px', color: '#0F172A', fontWeight: 500 }}>{r.total_distance_km?.toFixed(1)} km</td>
                <td style={{ padding: '12px 16px', color: '#0F172A', fontWeight: 500 }}>{r.total_duration_minutes?.toFixed(0)} min</td>
                <td style={{ padding: '12px 16px', color: '#0F172A', fontWeight: 500 }}>{r.estimated_fuel_liters?.toFixed(1)} L</td>
                <td style={{ padding: '12px 16px' }}>
                  {r.optimization_score
                    ? <Badge variant="green">{(r.optimization_score * 100).toFixed(0)}%</Badge>
                    : '—'}
                </td>
                <td style={{ padding: '12px 16px', color: '#64748B', fontSize: 11, fontWeight: 500 }}>
                  {format(new Date(r.created_at), 'dd MMM, HH:mm')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  )
}
