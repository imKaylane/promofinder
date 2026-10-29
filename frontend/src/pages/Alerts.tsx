import { useState, useEffect, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { userService } from '../services'
import { useAuth } from '../hooks/useAuth'
import type { PriceAlert } from '../types'
import { formatCurrency, formatDate } from '../utils/format'

export default function Alerts() {
  const { isAuthenticated } = useAuth()
  const [alerts, setAlerts] = useState<PriceAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [productId, setProductId] = useState('')
  const [targetPrice, setTargetPrice] = useState('')
  const [creating, setCreating] = useState(false)
  const [formError, setFormError] = useState('')

  useEffect(() => {
    if (!isAuthenticated) { setLoading(false); return }
    userService
      .getAlerts()
      .then(r => setAlerts(r.data))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false))
  }, [isAuthenticated])

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    if (!productId.trim() || !targetPrice) return
    setCreating(true)
    setFormError('')
    try {
      const { data } = await userService.createAlert(productId, parseFloat(targetPrice))
      setAlerts(prev => [data, ...prev])
      setProductId('')
      setTargetPrice('')
    } catch {
      setFormError('Erro ao criar alerta. Verifique o ID do produto.')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await userService.deleteAlert(id)
      setAlerts(prev => prev.filter(a => a.id !== id))
    } catch {
      // ignore
    }
  }

  if (!isAuthenticated) {
    return (
      <main className="max-w-xl mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-white mb-2">Alertas de Preço</h1>
        <p className="text-muted mb-6">Faça login para gerenciar seus alertas.</p>
        <Link to="/login" className="btn-primary">Entrar</Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">🔔 Alertas de Preço</h1>

      {/* Create alert form */}
      <div className="card mb-6">
        <h2 className="text-base font-semibold text-white mb-3">Novo alerta</h2>
        <form onSubmit={handleCreate} className="flex flex-col gap-3">
          <input
            className="input"
            placeholder="ID do produto (UUID do banco)"
            value={productId}
            onChange={e => setProductId(e.target.value)}
          />
          <div className="flex gap-3">
            <input
              className="input flex-1"
              placeholder="Preço alvo (R$)"
              type="number"
              min={0.01}
              step={0.01}
              value={targetPrice}
              onChange={e => setTargetPrice(e.target.value)}
            />
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? '...' : 'Criar Alerta'}
            </button>
          </div>
          {formError && <p className="text-danger text-sm">{formError}</p>}
        </form>
      </div>

      {/* Alerts list */}
      {loading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="card h-16 animate-pulse bg-border" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-muted">Você não tem alertas ativos.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {alerts.map(alert => (
            <div key={alert.id} className="card flex items-center justify-between gap-4">
              <div>
                <p className="text-white text-sm font-medium">
                  Produto: <span className="text-muted font-mono text-xs">{alert.product_id}</span>
                </p>
                <p className="text-accent font-bold">{formatCurrency(Number(alert.target_price))}</p>
                <p className="text-xs text-muted mt-0.5">
                  {alert.is_active
                    ? `Ativo — criado em ${formatDate(alert.created_at)}`
                    : '✅ Alerta disparado'}
                </p>
              </div>
              <button
                onClick={() => handleDelete(alert.id)}
                className="text-sm text-danger hover:text-red-300 transition-colors shrink-0"
              >
                Excluir
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}
