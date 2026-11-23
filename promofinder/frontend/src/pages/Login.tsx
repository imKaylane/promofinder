import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n'
import AppearanceControls from '../components/AppearanceControls'

export default function Login() {
  const { t } = useLanguage()
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (isAuthenticated) {
    navigate('/', { replace: true })
    return null
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError(t('login.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-20">
      <AppearanceControls />
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-accent font-bold text-3xl">⚡</span>
          <h1 className="mt-2 text-2xl font-bold text-foreground">{t('login.title')}</h1>
          <p className="mt-1 text-sm text-muted">{t('login.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="card flex flex-col gap-4">
          <div>
            <label className="text-sm text-muted mb-1 block">{t('login.email')}</label>
            <input
              className="input"
              type="email"
              placeholder={t('login.emailPlaceholder')}
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="text-sm text-muted mb-1 block">{t('login.password')}</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p className="text-danger text-sm">{error}</p>
          )}

          <button type="submit" className="btn-primary w-full py-2.5" disabled={loading}>
            {loading ? t('login.loading') : t('login.title')}
          </button>

          <p className="text-center text-sm text-muted">
            {t('login.noAccount')}{' '}
            <Link to="/register" className="text-accent hover:underline">
              {t('register.title')}
            </Link>
          </p>
        </form>
      </div>
    </main>
  )
}
