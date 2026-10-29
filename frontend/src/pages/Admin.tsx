import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminService } from '../services'
import { useAuth } from '../hooks/useAuth'
import type { User } from '../types'
import { formatDate } from '../utils/format'

export default function Admin() {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState<{ users: number; products: number; alerts: number } | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login', { replace: true }); return }
    if (user?.role !== 'admin') { navigate('/', { replace: true }); return }

    Promise.all([adminService.getStats(), adminService.getUsers()])
      .then(([statsRes, usersRes]) => {
        setStats(statsRes.data)
        setUsers(usersRes.data)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [isAuthenticated, user])

  const handleToggle = async (u: User) => {
    try {
      if (u.is_active) {
        await adminService.deactivateUser(u.id)
      } else {
        await adminService.activateUser(u.id)
      }
      setUsers(prev => prev.map(x => x.id === u.id ? { ...x, is_active: !x.is_active } : x))
    } catch {
      // ignore
    }
  }

  if (loading) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="card h-32 animate-pulse bg-border" />
      </main>
    )
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">⚙️ Painel Admin</h1>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: 'Usuários', value: stats.users },
            { label: 'Produtos', value: stats.products },
            { label: 'Alertas', value: stats.alerts },
          ].map(s => (
            <div key={s.label} className="card text-center">
              <p className="text-3xl font-bold text-accent">{s.value}</p>
              <p className="text-muted text-sm mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Users table */}
      <div className="card">
        <h2 className="text-base font-semibold text-white mb-4">Usuários</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left border-b border-border">
                <th className="pb-2 font-medium">Nome</th>
                <th className="pb-2 font-medium">E-mail</th>
                <th className="pb-2 font-medium">Papel</th>
                <th className="pb-2 font-medium">Cadastro</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b border-border/50 last:border-0">
                  <td className="py-2.5 text-white">{u.name}</td>
                  <td className="py-2.5 text-muted">{u.email}</td>
                  <td className="py-2.5">
                    <span className={`badge ${u.role === 'admin' ? 'text-violet-400 bg-violet/10' : 'text-muted bg-white/5'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-2.5 text-muted">{formatDate(u.created_at)}</td>
                  <td className="py-2.5">
                    <span className={`badge ${u.is_active ? 'text-success bg-success/10' : 'text-danger bg-danger/10'}`}>
                      {u.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="py-2.5">
                    {u.id !== user?.id && (
                      <button
                        onClick={() => handleToggle(u)}
                        className={`text-xs ${u.is_active ? 'text-danger' : 'text-success'} hover:underline`}
                      >
                        {u.is_active ? 'Desativar' : 'Ativar'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  )
}
