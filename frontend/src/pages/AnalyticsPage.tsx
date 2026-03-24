import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts'
import { Card, CardHeader } from '@/components/ui'

const weeklyData = [
  { day: 'Mon', deliveries: 312, fuel: 180, savings: 14 },
  { day: 'Tue', deliveries: 298, fuel: 172, savings: 16 },
  { day: 'Wed', deliveries: 341, fuel: 195, savings: 18 },
  { day: 'Thu', deliveries: 378, fuel: 201, savings: 19 },
  { day: 'Fri', deliveries: 402, fuel: 210, savings: 21 },
  { day: 'Sat', deliveries: 280, fuel: 155, savings: 17 },
  { day: 'Sun', deliveries: 195, fuel: 108, savings: 15 },
]

const etaAccuracy = [
  { hour: '06:00', accuracy: 91 }, { hour: '08:00', accuracy: 82 },
  { hour: '10:00', accuracy: 88 }, { hour: '12:00', accuracy: 85 },
  { hour: '14:00', accuracy: 90 }, { hour: '16:00', accuracy: 78 },
  { hour: '18:00', accuracy: 72 }, { hour: '20:00', accuracy: 89 },
]

const ttStyle = {
  background: 'var(--surface)', border: '1px solid var(--border)',
  borderRadius: 8, padding: '8px 12px', fontSize: 12,
  color: 'var(--text)', fontFamily: 'DM Sans, sans-serif',
}

export default function AnalyticsPage() {
  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 800, letterSpacing: '-0.5px' }}>
          Analytics
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 2 }}>
          Fleet performance & AI optimization metrics
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        {/* Deliveries + Fuel */}
        <Card>
          <CardHeader title="Weekly Deliveries & Fuel" subtitle="Last 7 days" />
          <div style={{ padding: '0 20px 20px' }}>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="day" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="left" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="right" orientation="right" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={ttStyle} />
                <Legend wrapperStyle={{ fontSize: 12, color: 'var(--muted)' }} />
                <Bar yAxisId="left" dataKey="deliveries" fill="var(--accent3)" radius={[3,3,0,0]} name="Deliveries" />
                <Bar yAxisId="right" dataKey="fuel" fill="var(--accent2)" radius={[3,3,0,0]} name="Fuel (L)" opacity={0.7} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* ETA Accuracy */}
        <Card>
          <CardHeader title="ETA Accuracy" subtitle="Model prediction quality by hour" />
          <div style={{ padding: '0 20px 20px' }}>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={etaAccuracy}>
                <defs>
                  <linearGradient id="etaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="hour" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis domain={[60, 100]} tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={ttStyle} formatter={(v: any) => [`${v}%`, 'Accuracy']} />
                <Area type="monotone" dataKey="accuracy" stroke="var(--accent)" fill="url(#etaGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Fuel Savings Trend */}
      <Card>
        <CardHeader title="AI Fuel Savings Trend" subtitle="% savings from route optimization vs. baseline" />
        <div style={{ padding: '0 20px 20px' }}>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="day" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[10, 25]} tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
              <Tooltip contentStyle={ttStyle} formatter={(v: any) => [`${v}%`, 'Fuel Saved']} />
              <Line type="monotone" dataKey="savings" stroke="var(--accent)" strokeWidth={2} dot={{ fill: 'var(--accent)', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  )
}
