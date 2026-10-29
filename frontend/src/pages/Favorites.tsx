import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { productService } from '../services'
import { useAuth } from '../hooks/useAuth'
import type { Favorite } from '../types'
import { formatDate } from '../utils/format'

export default function Favorites() {
  const { isAuthenticated } = useAuth()
  const [favorites, setFavorites] = useState<Favorite[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) { setLoading(false); return }
    productService
      .getFavorites()
      .then(r => setFavorites(r.data))
      .catch(() => setFavorites([]))
      .finally(() => setLoading(false))
  }, [isAuthenticated])

  const handleRemove = async (product_id: string) => {
    try {
      await productService.removeFavorite(product_id)
      setFavorites(prev => prev.filter(f => f.product_id !== product_id))
    } catch {
      // ignore
    }
  }

  if (!isAuthenticated) {
    return (
      <main className="max-w-xl mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-white mb-2">Favoritos</h1>
        <p className="text-muted mb-6">Faça login para gerenciar seus favoritos.</p>
        <Link to="/login" className="btn-primary">Entrar</Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">❤️ Meus Favoritos</h1>

      {loading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card h-16 animate-pulse bg-border" />
          ))}
        </div>
      ) : favorites.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-muted">Você ainda não tem favoritos.</p>
          <Link to="/search" className="text-accent hover:underline text-sm mt-2 block">
            Buscar produtos →
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {favorites.map(fav => (
            <div key={fav.id} className="card flex items-center justify-between gap-4">
              <div>
                <p className="text-white text-sm font-medium">
                  {fav.product?.name ?? fav.product_id}
                </p>
                {fav.product?.brand && (
                  <p className="text-xs text-muted">{fav.product.brand}</p>
                )}
                <p className="text-xs text-muted mt-0.5">Adicionado em {formatDate(fav.created_at)}</p>
              </div>
              <button
                onClick={() => handleRemove(fav.product_id)}
                className="text-sm text-danger hover:text-red-300 transition-colors shrink-0"
              >
                Remover
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}
