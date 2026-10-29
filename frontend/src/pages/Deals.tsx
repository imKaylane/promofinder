import { useState, useEffect } from 'react'
import { dealsService } from '../services'
import ProductCard from '../components/ProductCard'
import type { OfferWithDeal } from '../types'

export default function Deals() {
  const [deals, setDeals] = useState<OfferWithDeal[]>([])
  const [loading, setLoading] = useState(true)
  const [limit, setLimit] = useState(20)

  const load = async (l = limit) => {
    setLoading(true)
    try {
      const { data } = await dealsService.getDeals({ limit: l })
      setDeals(data)
    } catch {
      setDeals([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">🔥 Ofertas em Destaque</h1>
          <p className="text-muted text-sm mt-1">
            Produtos classificados pelo nosso motor de análise de preços.
          </p>
        </div>
        <select
          className="input w-auto"
          value={limit}
          onChange={e => { setLimit(Number(e.target.value)); load(Number(e.target.value)) }}
        >
          <option value={10}>10 itens</option>
          <option value={20}>20 itens</option>
          <option value={50}>50 itens</option>
        </select>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card h-40 animate-pulse bg-border" />
          ))}
        </div>
      ) : deals.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-muted text-lg">Nenhuma oferta disponível ainda.</p>
          <p className="text-sm text-muted mt-2">
            Use a busca ao vivo para pesquisar produtos e populamos o banco automaticamente.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {deals.map(offer => (
            <ProductCard key={offer.id} offer={offer} />
          ))}
        </div>
      )}
    </main>
  )
}
