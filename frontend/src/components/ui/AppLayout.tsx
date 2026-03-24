import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, Truck, Map, BarChart3, Zap, 
  LogOut, Shield, Brain
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authAPI } from '@/services/api'
import clsx from 'clsx'

interface NavItem {
  to: string
  icon: any
  label: string
  roles?: string[]
  badge?: number
}

const navItems: NavItem[] = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/fleet',     icon: Truck,           label: 'Fleet', roles: ['admin', 'manager', 'superadmin'] },
  { to: '/routes',    icon: Map,             label: 'Routes' },
  { to: '/optimize',  icon: Zap,             label: 'Optimize', roles: ['admin', 'manager', 'superadmin'] },
  { to: '/analytics', icon: BarChart3,       label: 'Analytics', roles: ['admin', 'manager', 'superadmin'] },
  { to: '/ai-hub',    icon: Brain,           label: 'AI Intelligence', roles: ['admin', 'superadmin'] },
  { to: '/superadmin', icon: Shield,          label: 'Superadmin', roles: ['superadmin'] },
]

export default function AppLayout() {
  const clearAuth = useAuthStore(s => s.clearAuth)
  const role = useAuthStore(s => s.role)
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await authAPI.logout()
    } catch (e) {
      console.error('Logout error', e)
    }
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <div className="bg-mesh opacity-5" />
      <div className="bg-grid opacity-10" />

      {/* Sidebar */}
      <aside className="fixed left-0 top-0 bottom-0 w-[260px] bg-white border-r border-slate-200 flex flex-col py-8 z-[100] shadow-sm">
        {/* Logo */}
        <div className="px-8 mb-12">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-yellow-400 rounded-2xl flex items-center justify-center shadow-[0_4px_16px_rgba(249,201,53,0.3)]">
              <Zap size={24} className="text-slate-900 fill-current" />
            </div>
            <div>
              <div className="font-display font-black text-2xl text-slate-900 tracking-tighter uppercase leading-none">RouteIQ</div>
              <div className="text-[10px] font-black text-yellow-600 uppercase tracking-[0.2em] mt-1 ml-0.5">Fleet Core</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-4 space-y-2">
          {navItems
            .filter(item => !item.roles || item.roles.includes(role || ''))
            .map(({ to, icon: Icon, label, badge }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => clsx(
                'flex items-center gap-4 px-5 py-4 rounded-2xl text-sm transition-all relative group overflow-hidden',
                isActive ? 'text-slate-900 font-bold bg-slate-100/80 shadow-sm' : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100/50'
              )}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-yellow-400 shadow-[2px_0_8px_rgba(249,201,53,0.4)]" />
                  )}
                  <Icon size={20} className={clsx('transition-all duration-300', isActive ? 'text-yellow-500 scale-110' : 'text-slate-400 group-hover:text-slate-600')} />
                  <span className="flex-1 tracking-tight">{label}</span>
                  {badge && (
                    <span className="bg-yellow-400 text-slate-900 text-[10px] font-black px-2 py-0.5 rounded-full shadow-sm">
                      {badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User Info & Bottom */}
        <div className="px-6 mt-auto pt-6 border-t border-slate-200">
          <button 
            className="flex items-center gap-4 w-full px-5 py-4 rounded-2xl text-sm font-bold text-slate-500 hover:text-red-400 hover:bg-red-400/10 transition-all group"
            onClick={handleLogout}
          >
            <LogOut size={20} className="group-hover:-translate-x-1 transition-transform" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-[240px] flex-1 p-8 min-h-screen">
        <div className="max-w-7xl mx-auto animate-fade-up">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
