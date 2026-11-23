import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../services/api'
import { useLanguage } from '../i18n'
import type { TranslationKey } from '../i18n'
import AppearanceControls from '../components/AppearanceControls'

export default function MercadoLivreCallback() {
  const { t } = useLanguage()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'connecting' | 'connected'>('connecting')
  const [error, setError] = useState<TranslationKey | null>(null)
  const submitted = useRef(false)

  useEffect(() => {
    if (submitted.current) return
    submitted.current = true

    const authorizationError = searchParams.get('error')
    const code = searchParams.get('code')
    const state = searchParams.get('state')

    if (authorizationError) {
      setError('meli.authorizationError')
      return
    }
    if (!code || !state) {
      setError('meli.incomplete')
      return
    }

    window.history.replaceState({}, '', window.location.pathname)
    api.post('/auth/meli/exchange', { code, state })
      .then(() => setStatus('connected'))
      .catch(() => setError('meli.failed'))
  }, [searchParams, t])

  return (
    <main className="mx-auto max-w-xl px-4 py-20 text-center">
      <AppearanceControls />
      <h1 className="mb-3 text-2xl font-bold">{t('meli.title')}</h1>
      {error
        ? <p className="mb-6 text-danger">{t(error)}</p>
        : <p className="mb-6 text-muted">{t(status === 'connected' ? 'meli.connected' : 'meli.connecting')}</p>}
      <Link to="/profile" className="btn-primary">{t('meli.backProfile')}</Link>
    </main>
  )
}
