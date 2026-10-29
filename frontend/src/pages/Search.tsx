import { useState, FormEvent } from 'react'
import { productService } from '../services'
import ProductCard from '../components/ProductCard'
import type { MeliItem } from '../types'

export default function Search() {
  const [query, setQuery] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [condition, setCondition] = useState('')
  const [sort, setSort] = useState('relevance')
  const [results, setResults] = useState<MeliItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    try {
      const { data } = await productService.searchLive({
        q: query,
        min_price: minPrice || undefined,
        max_price: maxPrice || undefined,
        condition: condition || undefined,
        sort,
        limit: 24,
        offset: 0,
      })
      setResults(data.results)
      setTotal(data.total)
      setSearched(true)
    } catch {
      setError('Erro ao buscar produtos. Verifique sua conexão e tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Busca Avançada</h1>

      <form onSubmit={handleSubmit} className="card mb-6 flex flex-col gap-4">
        <div className="flex gap-3">
          <input
            className="input flex-1"
            placeholder="Ex: RTX 4060, Ryzen 7, iPhone 15..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <button type="submit" className="btn-primary px-6" disabled={loading}>
            {loading ? '...' : 'Buscar'}
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <input
            className="input"
            placeholder="Preço mínimo (R$)"
            type="number"
            min={0}
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
          />
          <input
            className="input"
            placeholder="Preço máximo (R$)"
            type="number"
            min={0}
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
          />
          <select className="input" value={condition} onChange={e => setCondition(e.target.value)}>
            <option value="">Condição</option>
            <option value="new">Novo</option>
            <option value="used">Usado</option>
          </select>
          <select className="input" value={sort} onChange={e => setSort(e.target.value)}>
            <option value="relevance">Relevância</option>
            <option value="price_asc">Menor preço</option>
            <option value="price_desc">Maior preço</option>
          </select>
        </div>
      </form>

      {error && (
        <div className="bg-danger/10 border border-danger/30 rounded-lg px-4 py-3 text-danger text-sm mb-4">
          {error}
        </div>
      )}

      {searched && (
        <p className="text-sm text-muted mb-4">
          {total.toLocaleString('pt-BR')} resultado{total !== 1 ? 's' : ''} para "{query}"
        </p>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {results.map(item => (
            <ProductCard key={item.id} item={item} />
          ))}
        </div>
      )}

      {searched && results.length === 0 && !loading && (
        <div className="card text-center py-12">
          <p className="text-muted">Nenhum resultado encontrado.</p>
          <p className="text-sm text-muted mt-1">Tente termos mais genéricos ou ajuste os filtros.</p>
        </div>
      )}
    </main>
  )
}
