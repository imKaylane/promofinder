import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n'
import AppearanceControls from '../components/AppearanceControls'

export default function Register() {
  const { t } = useLanguage()
  const { register, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
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
    if (password.length < 8) {
      setError(t('register.passwordShort'))
      return
    }
    setLoading(true)
    setError('')
    try {
      await register(name, email, password)
      navigate('/')
    } catch (err: unknown) {
      const response = (err as {
        response?: { status?: number; data?: { detail?: unknown } }
      }).response
      const detail = response?.data?.detail
      if (detail === 'E-mail already registered.') {
        setError(t('register.emailExists'))
      } else if (Array.isArray(detail)) {
        const fields = detail.flatMap(issue => {
          if (typeof issue !== 'object' || issue === null || !('loc' in issue) || !Array.isArray(issue.loc)) {
            return []
          }
          const field = issue.loc[issue.loc.length - 1]
          return typeof field === 'string' ? [field] : []
        })
        if (fields.includes('email')) {
          setError(t('register.emailInvalid'))
        } else if (fields.includes('name')) {
          setError(t('register.nameShort'))
        } else if (fields.includes('password')) {
          setError(t('register.passwordLength'))
        } else {
          setError(t('register.invalidForm'))
        }
      } else if (response?.status === 422) {
        setError(t('register.invalidForm'))
      } else {
        setError(t('register.error'))
      }
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
          <h1 className="mt-2 text-2xl font-bold text-foreground">{t('register.title')}</h1>
          <p className="mt-1 text-sm text-muted">{t('register.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="card flex flex-col gap-4">
          <div>
            <label className="text-sm text-muted mb-1 block">{t('register.name')}</label>
            <input
              className="input"
              placeholder={t('register.namePlaceholder')}
              value={name}
              onChange={e => setName(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="text-sm text-muted mb-1 block">{t('login.email')}</label>
            <input
              className="input"
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-sm text-muted mb-1 block">{t('login.password')}</label>
            <input
              className="input"
              type="password"
              placeholder={t('register.passwordHint')}
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={8}
              maxLength={72}
            />
          </div>

          {error && <p className="text-danger text-sm">{error}</p>}

          <button type="submit" className="btn-primary w-full py-2.5" disabled={loading}>
            {loading ? t('register.loading') : t('register.title')}
          </button>

          <p className="text-center text-sm text-muted">
            {t('register.haveAccount')}{' '}
            <Link to="/login" className="text-accent hover:underline">
              {t('login.title')}
            </Link>
          </p>
        </form>
      </div>
    </main>
  )
}
