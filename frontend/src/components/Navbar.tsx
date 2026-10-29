import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const navClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm transition-colors ${isActive ? 'text-white font-medium' : 'text-muted hover:text-white'}`

  return (
    <header className="sticky top-0 z-50 bg-surface/90 backdrop-blur border-b border-border">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-6">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <span className="text-accent font-bold text-lg">⚡</span>
          <span className="font-bold text-white text-base hidden sm:block">TechDeals AI</span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-5 flex-1">
          <NavLink to="/deals" className={navClass}>Ofertas</NavLink>
          <NavLink to="/search" className={navClass}>Buscar</NavLink>
          <NavLink to="/ai-search" className={navClass}>
            <span className="flex items-center gap-1">
              <span className="text-violet-400">✦</span> IA
            </span>
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/favorites" className={navClass}>Favoritos</NavLink>
              <NavLink to="/alerts" className={navClass}>Alertas</NavLink>
            </>
          )}
          {user?.role === 'admin' && (
            <NavLink to="/admin" className={navClass}>Admin</NavLink>
          )}
        </nav>

        {/* Auth */}
        <div className="flex items-center gap-3 shrink-0">
          {isAuthenticated ? (
            <>
              <span className="text-sm text-muted hidden md:block">{user?.name}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-muted hover:text-white transition-colors"
              >
                Sair
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-muted hover:text-white transition-colors">
                Entrar
              </Link>
              <Link to="/register" className="btn-primary text-sm py-1.5 px-3">
                Cadastrar
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
