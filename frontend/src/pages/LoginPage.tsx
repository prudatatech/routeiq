import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, Eye, EyeOff, ShieldCheck, UserCog, User, Truck } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authAPI } from '@/services/api'
import { Card, Button, Spinner } from '@/components/ui'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const setAuth = useAuthStore(s => s.setAuth)
  const navigate = useNavigate()

  const handleLogin = async (e?: React.FormEvent, customEmail?: string, customPass?: string) => {
    e?.preventDefault()
    setLoading(true)
    const targetEmail = customEmail || email
    const targetPass = customPass || password
    
    try {
      const data = await authAPI.login(targetEmail, targetPass)
      setAuth(data.access_token, data.refresh_token, data.role)
      toast.success(`Welcome back, ${data.role}!`)
      if (data.role === 'superadmin') {
        navigate('/superadmin')
      } else {
        navigate('/dashboard')
      }
    } catch {
      // toast is already handled by axios interceptor or global handler
    } finally {
      setLoading(false)
    }
  }

  const QUICK_LOGINS = [
    { role: 'superadmin', icon: ShieldCheck, email: 'superadmin@routeiq.io', pass: 'SuperAdmin1234!', color: 'text-yellow-400' },
    { role: 'admin', icon: UserCog, email: 'admin@routeiq.io', pass: 'Admin1234!', color: 'text-white' },
    { role: 'manager', icon: User, email: 'manager@routeiq.io', pass: 'Manager1234!', color: 'text-slate-400' },
    { role: 'driver', icon: Truck, email: 'driver@routeiq.io', pass: 'Driver1234!', color: 'text-yellow-600' },
  ]

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-yellow-400/20 blur-[120px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[420px] space-y-10 relative z-10 animate-fade-in">
        {/* Branding */}
        <div className="text-center space-y-3">
          <div className="inline-flex w-20 h-20 bg-yellow-400 rounded-3xl items-center justify-center shadow-[0_8px_32px_rgba(249,201,53,0.3)] rotate-3 hover:rotate-0 transition-transform duration-500">
            <Zap size={44} className="text-slate-900 fill-current" strokeWidth={2.5} />
          </div>
          <h1 className="font-display text-6xl font-black text-slate-900 tracking-tighter uppercase leading-none pt-4">
            Route<span className="text-yellow-500">IQ</span>
          </h1>
          <p className="text-slate-500 font-bold uppercase tracking-[0.3em] text-[10px]">
            Hyper-Efficient Fleet Core
          </p>
        </div>

        {/* Login Card */}
        <Card className="p-8 border-slate-200 bg-white shadow-xl backdrop-blur-xl">
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest ml-1">Command Control ID</label>
              <input
                type="email"
                placeholder="email@routeiq.io"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 text-sm focus:outline-none focus:border-yellow-400/50 transition-all font-bold placeholder:text-slate-400 shadow-sm"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest ml-1">Access Pass-Key</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 text-sm focus:outline-none focus:border-yellow-400/50 transition-all font-bold placeholder:text-slate-400 shadow-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <Button
              variant="accent"
              className="w-full py-7 rounded-2xl text-base shadow-[0_20px_40px_rgba(249,201,53,0.15)] group"
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <Spinner size={20} />
              ) : (
                <span className="flex items-center gap-2">
                  ACTIVATE SYSTEM <Zap size={16} className="fill-current" />
                </span>
              )}
            </Button>
          </form>
        </Card>

        {/* Demo Roles / Quick Login */}
        <div className="space-y-4 pt-4">
          <div className="flex items-center gap-4 px-4">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.3em] whitespace-nowrap">Rapid Demo Access</span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {QUICK_LOGINS.map(({ role, icon: Icon, email: e, pass: p }) => (
              <button
                key={role}
                onClick={() => handleLogin(undefined, e, p)}
                disabled={loading}
                className="group p-4 bg-slate-50 border border-slate-200 rounded-2xl hover:bg-slate-100 hover:border-yellow-400/50 transition-all text-left relative overflow-hidden shadow-sm"
              >
                <Icon size={20} className={clsx("mb-2 group-hover:scale-110 transition-transform text-slate-900")} />
                <div className="font-display font-black text-xs text-slate-900 uppercase tracking-tighter">{role}</div>
                <div className="text-[8px] font-bold text-slate-500 uppercase tracking-widest mt-0.5">Quick Link</div>
                <div className="absolute -right-2 -bottom-2 opacity-[0.03] rotate-12 group-hover:rotate-0 transition-transform text-slate-900">
                  <Icon size={48} />
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Meta */}
      <div className="mt-12 text-[10px] font-bold text-slate-400 uppercase tracking-[0.5em] animate-pulse">
         Core v1.0 // Intelligence Grid Active
      </div>
    </div>
  )
}
