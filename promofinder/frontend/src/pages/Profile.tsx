import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'
import { useLanguage } from '../i18n'

export default function Profile() {
  const { t } = useLanguage()
  const { user, isAuthenticated } = useAuth()
  const [meliConnected, setMeliConnected] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) return
    api.get('/auth/meli/status')
      .then(({ data }) => setMeliConnected(data.connected))
      .catch(() => setMeliConnected(false))
  }, [isAuthenticated])

  if (!isAuthenticated || !user) {
    return (
      <main className="mx-auto max-w-xl px-4 py-20 text-center">
        <h1 className="mb-2 text-2xl font-bold">{t('profile.title')}</h1>
        <p className="mb-6 text-muted">{t('profile.loginRequired')}</p>
        <Link to="/login" className="btn-primary">Entrar</Link>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="mb-8">
        <p className="mb-2 text-sm font-medium text-accent">{t('profile.account')}</p>
        <h1 className="text-3xl font-bold">{t('profile.title')}</h1>
        <p className="mt-2 text-muted">{t('profile.description')}</p>
      </div>

      <section className="card">
        <h2 className="mb-5 text-lg font-semibold">{t('profile.info')}</h2>
        <dl className="grid gap-5 sm:grid-cols-2">
          <div>
            <dt className="text-sm text-muted">{t('register.name')}</dt>
            <dd className="mt-1 font-medium">{user.name}</dd>
          </div>
          <div>
            <dt className="text-sm text-muted">E-mail</dt>
            <dd className="mt-1 font-medium">{user.email}</dd>
          </div>
          <div>
            <dt className="text-sm text-muted">{t('profile.accountType')}</dt>
            <dd className="mt-1 font-medium">{user.role === 'admin' ? t('profile.admin') : t('profile.user')}</dd>
          </div>
          <div>
            <dt className="text-sm text-muted">{t('profile.accountLabel')}</dt>
            <dd className="mt-1 font-medium">{user.is_active ? t('profile.active') : t('profile.inactive')}</dd>
          </div>
        </dl>
      </section>

      <section className="card mt-5">
        <h2 className="text-lg font-semibold">{t('profile.meli')}</h2>
        <p className="mt-2 text-sm text-muted">
          {meliConnected
            ? t('profile.meliConnected')
            : t('profile.meliNotConnected')}
        </p>
        <a href="/api/v1/auth/meli/authorize" className="btn-primary mt-4 inline-block">
          {meliConnected ? t('profile.connectAgain') : t('profile.connectMeli')}
        </a>
      </section>

      <section className="card mt-5">
        <h2 className="text-lg font-semibold">{t('profile.preferences')}</h2>
        <p className="mt-2 text-sm text-muted">
          {t('profile.themeDescription')}
        </p>
      </section>
    </main>
  )
}
