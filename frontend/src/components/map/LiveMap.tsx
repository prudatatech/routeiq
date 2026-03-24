import { useEffect, useRef } from 'react'

interface Vehicle {
  id: string
  plate_number: string
  latitude?: number
  longitude?: number
  status: string
  vehicle_type?: string
}

// Major Indian city delivery positions for demo
const INDIA_POSITIONS: { lng: number; lat: number; city: string }[] = [
  { lng: 77.2090, lat: 28.6139, city: 'Delhi' },
  { lng: 72.8777, lat: 19.0760, city: 'Mumbai' },
  { lng: 80.2707, lat: 13.0827, city: 'Chennai' },
  { lng: 88.3639, lat: 22.5726, city: 'Kolkata' },
  { lng: 77.5946, lat: 12.9716, city: 'Bangalore' },
  { lng: 78.4867, lat: 17.3850, city: 'Hyderabad' },
  { lng: 73.8567, lat: 18.5204, city: 'Pune' },
  { lng: 75.7873, lat: 26.9124, city: 'Jaipur' },
  { lng: 72.5714, lat: 23.0225, city: 'Ahmedabad' },
  { lng: 85.8245, lat: 20.2961, city: 'Bhubaneswar' },
]

const STATUS_COLORS: Record<string, string> = {
  on_route:    '#F9C935',
  available:   '#10b981',
  idle:        '#94a3b8',
  maintenance: '#f59e0b',
  offline:     '#ef4444',
}

const VEHICLE_EMOJI: Record<string, string> = {
  truck: '🚛',
  van:   '🚐',
  bike:  '🏍️',
  car:   '🚗',
}

export default function LiveMap({ vehicles }: { vehicles: Vehicle[] }) {
  const mapRef    = useRef<HTMLDivElement>(null)
  const mapInst   = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const intervalRef = useRef<any>(null)

  useEffect(() => {
    if (!mapRef.current || mapInst.current) return

    import('maplibre-gl').then(({ default: maplibregl }) => {
      const map = new maplibregl.Map({
        container: mapRef.current!,
        style: {
          version: 8,
          sources: {
            osm: {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '© OpenStreetMap',
            },
          },
          layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
        } as any,
        center: [81.0, 22.5],   // Centre of India
        zoom:   4.2,
        minZoom: 3,
        maxZoom: 14,
        attributionControl: false,
      })

      map.on('load', () => {
        // Build vehicle list from props or use Indian city demos
        const list: any[] = vehicles.length > 0
          ? vehicles.map((v, i) => ({
              ...v,
              lat: v.latitude  ?? INDIA_POSITIONS[i % INDIA_POSITIONS.length].lat,
              lng: v.longitude ?? INDIA_POSITIONS[i % INDIA_POSITIONS.length].lng,
              city: INDIA_POSITIONS[i % INDIA_POSITIONS.length].city,
            }))
          : INDIA_POSITIONS.slice(0, 8).map((p, i) => ({
              id: 'demo-' + i,
              plate_number: ['DL-1001','MH-9001','TN-2345','WB-1234','KA-5678','TS-4321','MH-4567','RJ-8901'][i],
              vehicle_type: ['truck','van','truck','bike','truck','van','truck','car'][i],
              status: ['on_route','available','on_route','idle','on_route','maintenance','on_route','available'][i],
              lat: p.lat,
              lng: p.lng,
              city: p.city,
            }))

        // Add markers
        list.forEach((v) => {
          const color   = STATUS_COLORS[v.status] || '#94a3b8'
          const emoji   = VEHICLE_EMOJI[v.vehicle_type] || '🚛'
          const el      = document.createElement('div')
          el.innerHTML  = `
            <div style="
              width:44px;height:44px;
              background:${color}22;
              border:2px solid ${color};
              border-radius:14px;
              display:flex;align-items:center;justify-content:center;
              font-size:22px;cursor:pointer;position:relative;
              box-shadow:0 4px 20px ${color}44;
              transition:transform 0.25s;
            " onmouseover="this.style.transform='scale(1.25)'" onmouseout="this.style.transform='scale(1)'">
              ${emoji}
              <div style="
                position:absolute;bottom:-28px;left:50%;transform:translateX(-50%);
                background:#fff;border:1px solid ${color}55;
                padding:2px 8px;border-radius:8px;font-size:10px;
                font-family:'Space Grotesk',sans-serif;font-weight:900;
                color:#0f172a;white-space:nowrap;
                box-shadow:0 2px 8px rgba(0,0,0,0.15);z-index:20;
              ">${v.plate_number}</div>
            </div>`

          const marker = new maplibregl.Marker({ element: el })
            .setLngLat([v.lng, v.lat])
            .addTo(map)

          markersRef.current.push({ marker, v, baseLat: v.lat, baseLng: v.lng })
        })

        // Animate markers (simulate live movement)
        intervalRef.current = setInterval(() => {
          markersRef.current.forEach(({ marker, v, baseLat, baseLng }, i) => {
            if (v.status === 'on_route') {
              const t   = Date.now() / 1000
              const jitter = 0.04
              const newLat = baseLat + Math.sin(t * 0.2 + i) * jitter
              const newLng = baseLng + Math.cos(t * 0.15 + i * 1.3) * jitter
              marker.setLngLat([newLng, newLat])
            }
          })
        }, 1200)
      })

      mapInst.current = map
    })

    return () => {
      clearInterval(intervalRef.current)
      mapInst.current?.remove()
      mapInst.current   = null
      markersRef.current = []
    }
  }, [])

  return (
    <div
      ref={mapRef}
      style={{
        width: '100%',
        height: 400,
        borderRadius: 16,
        overflow: 'hidden',
        border: '1px solid #e2e8f0',
      }}
    />
  )
}
