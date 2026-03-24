import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Search, User } from 'lucide-react'
import { usersAPI } from '@/services/api'
import { Card, Badge, Button, Spinner } from '@/components/ui'
import toast from 'react-hot-toast'

const ROLE_OPTIONS = ['admin', 'manager', 'driver', 'superadmin']

export default function SuperadminPage() {
  const [search, setSearch] = useState('')
  const queryClient = useQueryClient()

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: usersAPI.list,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => usersAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success('User updated successfully')
    },
  })

  const filtered = users.filter((u: any) =>
    u.email.toLowerCase().includes(search.toLowerCase()) ||
    u.full_name.toLowerCase().includes(search.toLowerCase())
  )

  const handleRoleChange = (userId: string, newRole: string) => {
    updateMutation.mutate({ id: userId, data: { role: newRole } })
  }

  const toggleActive = (userId: string, currentStatus: boolean) => {
    updateMutation.mutate({ id: userId, data: { is_active: !currentStatus } })
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div className="space-y-1">
          <h1 className="font-heading font-bold text-3xl text-white tracking-tight">Platform Administration</h1>
          <p className="text-slate-500 text-sm flex items-center gap-2">
            <Shield size={14} className="text-purple-500" />
            Manage system users, access levels, and security policies
          </p>
        </div>
      </div>

      {/* Filters + Search */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-2 w-full max-w-sm focus-within:border-purple-400/30 transition-colors">
          <Search size={16} className="text-slate-500" />
          <input
            placeholder="Search users by email or name..."
            className="bg-transparent border-none outline-none text-sm text-white w-full placeholder:text-slate-600"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Users Table */}
      <Card className="border-white/5 shadow-2xl relative">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-white/5">
                {['User', 'Role', 'Status', 'Joined', 'Actions'].map(h => (
                  <th key={h} className="px-6 py-4 text-left text-[10px] font-bold text-slate-500 uppercase tracking-widest">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-20 text-center">
                    <Spinner size={32} />
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-20 text-center text-slate-500 text-xs">
                    No users found
                  </td>
                </tr>
              ) : (
                filtered.map((u: any) => (
                  <tr key={u.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 border border-white/5">
                          <User size={14} />
                        </div>
                        <div>
                          <div className="text-sm font-bold text-white">{u.full_name}</div>
                          <div className="text-[10px] text-slate-500 mono">{u.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        className="bg-slate-900 border border-white/10 rounded-lg px-2 py-1 text-xs text-white outline-none focus:border-purple-500/50"
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        disabled={updateMutation.isPending}
                      >
                        {ROLE_OPTIONS.map(r => (
                          <option key={r} value={r}>{r.toUpperCase()}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={u.is_active ? 'green' : 'orange'}>
                        {u.is_active ? 'ACTIVE' : 'DEACTIVATED'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-[10px] text-slate-500 mono">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <Button
                        size="sm"
                        variant={u.is_active ? 'ghost' : 'accent'}
                        className="text-[10px]"
                        onClick={() => toggleActive(u.id, u.is_active)}
                        disabled={updateMutation.isPending}
                      >
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
