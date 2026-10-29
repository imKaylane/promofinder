import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { aiService } from '../services'
import { useAuth } from '../hooks/useAuth'
import ProductCard from '../components/ProductCard'
import type { AISearchResponse, MeliItem } from '../types'

export default function AISearch() {
  const { isAuthenticated } = useAuth()
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<AISearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    try {
      const { data } = await aiService.search(query)
      setResponse(data)
    } catch {
      setError('Erro ao processar busca. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <main className="max-w-xl mx-auto px-4 py-20 text-center">
        <span className="text-4xl mb-4 block">✦</span>
        <h1 className="text-2xl font-bold text-white mb-2">Busca com IA</h1>
        <p className="text-muted mb-6">Faça login para usar a busca inteligente com inteligência artificial.</p>
        <Link to="/login" className="btn-primary">Entrar</Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-violet-400">✦</span>
        <h1 className="text-2xl font-bold text-white">Busca com Inteligência Artificial</h1>
      </div>
      <p className="text-muted mb-6">
        Descreva o que você procura em linguagem natural. A IA extrai os filtros e busca no Mercado Livre.
      </p>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <input
          className="input flex-1"
          placeholder="Ex: Processador Ryzen 7 até R$ 1.500, placa de vídeo com bom custo-benefício…"
          value={query}
          onChange={e => setQuery(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-primary px-6 min-w-[80px]" disabled={loading || !query.trim()}>
          {loading ? (
            <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            'Buscar'
          )}
        </button>
      </form>

      {/* Examples */}
      {!response && !loading && (
        <div className="flex flex-wrap gap-2 mb-8">
          {[
            'Processador Ryzen 7 até R$ 1.500',
            'Placa de vídeo com bom custo-benefício',
            'Notebook gamer até R$ 4.000',
            'SSD NVMe 1TB',
          ].map(ex => (
            <button
              key={ex}
              onClick={() => setQuery(ex)}
              className="badge bg-surface border border-border text-muted hover:text-white hover:border-accent/50 transition-colors px-3 py-1 cursor-pointer"
            >
              {ex}
            </button>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-danger/10 border border-danger/30 rounded-lg px-4 py-3 text-danger text-sm mb-4">
          {error}
        </div>
      )}

      {response && (
        <div className="flex flex-col gap-6">
          {/* Interpreted query */}
          <div className="card">
            <p className="text-xs text-muted mb-1">Consulta interpretada pela IA</p>
            <p className="text-white font-medium">"{response.interpreted_query}"</p>
            {!response.ai_available && (
              <p className="text-xs text-warning mt-2">
                ⚠ IA não configurada — filtros extraídos por regras locais.
              </p>
            )}
          </div>

          {/* AI Summary */}
          {response.ai_summary && (
            <div className="card bg-violet/5 border-violet/20">
              <p className="text-xs text-violet-400 mb-2">✦ Análise da IA</p>
              <p className="text-white text-sm leading-relaxed whitespace-pre-wrap">{response.ai_summary}</p>
            </div>
          )}

          {/* Results */}
          <div>
            <p className="text-sm text-muted mb-3">{response.products.length} produto(s) encontrado(s)</p>
            {response.products.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {response.products.map((item: MeliItem) => (
                  <ProductCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <div className="card text-center py-10">
                <p className="text-muted">Nenhum produto encontrado. Tente reformular a busca.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  )
}
