import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Register() {
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
      setError('A senha deve ter pelo menos 8 caracteres.')
      return
    }
    setLoading(true)
    setError('')
    try {
      await register(name, email, password)
      navigate('/')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      const detail = axiosErr.response?.data?.detail
      setError(detail === 'E-mail already registered.' ? 'Este e-mail já está cadastrado.' : 'Erro ao criar conta.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-accent font-bold text-3xl">⚡</span>
          <h1 className="text-2xl font-bold text-white mt-2">Criar conta</h1>
          <p className="text-muted text-sm mt-1">Comece a monitorar ofertas gratuitamente</p>
        </div>

        <form onSubmit={handleSubmit} className="card flex flex-col gap-4">
          <div>
            <label className="text-sm text-muted mb-1 block">Nome</label>
            <input
              className="input"
              placeholder="Seu nome"
              value={name}
              onChange={e => setName(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="text-sm text-muted mb-1 block">E-mail</label>
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
            <label className="text-sm text-muted mb-1 block">Senha</label>
            <input
              className="input"
              type="password"
              placeholder="Mínimo 8 caracteres"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>

          {error && <p className="text-danger text-sm">{error}</p>}

          <button type="submit" className="btn-primary w-full py-2.5" disabled={loading}>
            {loading ? 'Criando conta…' : 'Criar conta'}
          </button>

          <p className="text-center text-sm text-muted">
            Já tem conta?{' '}
            <Link to="/login" className="text-accent hover:underline">
              Entrar
            </Link>
          </p>
        </form>
      </div>
    </main>
  )
}
