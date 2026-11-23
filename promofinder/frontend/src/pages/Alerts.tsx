import { useState, useEffect, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { userService } from '../services'
import { useAuth } from '../hooks/useAuth'
import type { PriceAlert } from '../types'
import { formatCurrency, formatDate } from '../utils/format'
import { useLanguage } from '../i18n'

export default function Alerts() {
  const { t, locale } = useLanguage()
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
      setFormError(t('alerts.error'))
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
        <h1 className="mb-2 text-2xl font-bold text-foreground">{t('alerts.title')}</h1>
        <p className="mb-6 text-muted">{t('alerts.loginRequired')}</p>
        <Link to="/login" className="btn-primary">Entrar</Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-foreground">🔔 {t('alerts.title')}</h1>

      {/* Create alert form */}
      <div className="card mb-6">
        <h2 className="mb-3 text-base font-semibold">{t('alerts.new')}</h2>
        <form onSubmit={handleCreate} className="flex flex-col gap-3">
          <input
            className="input"
            aria-label={t('alerts.productId')}
            placeholder={t('alerts.productId')}
            value={productId}
            onChange={e => setProductId(e.target.value)}
          />
          <div className="flex gap-3">
            <input
              className="input flex-1"
              aria-label={t('alerts.targetPrice')}
              placeholder={t('alerts.targetPrice')}
              type="number"
              min={0.01}
              step={0.01}
              value={targetPrice}
              onChange={e => setTargetPrice(e.target.value)}
            />
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? '...' : t('alerts.create')}
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
          <p className="text-muted">{t('alerts.none')}</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {alerts.map(alert => (
            <div key={alert.id} className="card flex items-center justify-between gap-4">
              <div>
                <p className="text-foreground text-sm font-medium">
                  {t('alerts.product')} <span className="font-mono text-xs text-muted">{alert.product_id}</span>
                </p>
                <p className="font-bold text-accent">{formatCurrency(Number(alert.target_price), 'BRL', locale)}</p>
                <p className="text-xs text-muted mt-0.5">
                  {alert.is_active
                    ? t('alerts.activeCreated', { date: formatDate(alert.created_at, locale) })
                    : t('alerts.triggered')}
                </p>
              </div>
              <button
                onClick={() => handleDelete(alert.id)}
                className="shrink-0 text-sm text-danger transition-colors hover:opacity-80"
              >
                {t('alerts.delete')}
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}
