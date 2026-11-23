import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { aiService } from '../services'
import { useAuth } from '../hooks/useAuth'
import ProductCard from '../components/ProductCard'
import type { AISearchResponse, MeliItem } from '../types'
import { useLanguage } from '../i18n'

const examples = [
  { label: 'ai.example1', query: 'Processador Ryzen 7 até R$ 1.500' },
  { label: 'ai.example2', query: 'Placa de vídeo com bom custo-benefício' },
  { label: 'ai.example3', query: 'Notebook gamer até R$ 4.000' },
  { label: 'ai.example4', query: 'SSD NVMe 1TB' },
] as const

export default function AISearch() {
  const { t, locale } = useLanguage()
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
      setError(t('ai.error'))
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <main className="max-w-xl mx-auto px-4 py-20 text-center">
        <span className="text-4xl mb-4 block">✦</span>
        <h1 className="mb-2 text-2xl font-bold text-foreground">{t('ai.shortTitle')}</h1>
        <p className="mb-6 text-muted">{t('ai.loginRequired')}</p>
        <Link to="/login" className="btn-primary">{t('shell.login')}</Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-violet">✦</span>
        <h1 className="text-2xl font-bold text-foreground">{t('ai.title')}</h1>
      </div>
      <p className="text-muted mb-6">
        {t('ai.description')}
      </p>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <input
          className="input flex-1"
          placeholder={t('ai.example')}
          value={query}
          onChange={e => setQuery(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-primary px-6 min-w-[80px]" disabled={loading || !query.trim()}>
          {loading ? (
            <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            t('search.submit')
          )}
        </button>
      </form>

      {/* Examples */}
      {!response && !loading && (
        <div className="flex flex-wrap gap-2 mb-8">
          {examples.map(ex => (
            <button
              key={ex.label}
              onClick={() => setQuery(ex.query)}
              className="badge bg-surface border border-border text-muted hover:text-accent hover:border-accent/50 transition-colors px-3 py-1 cursor-pointer"
            >
              {t(ex.label)}
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
            <p className="text-xs text-muted mb-1">{t('ai.interpreted')}</p>
            <p className="font-medium text-foreground">"{response.interpreted_query}"</p>
            {!response.ai_available && (
              <p className="text-xs text-warning mt-2">
                {t('ai.notConfigured')}
              </p>
            )}
          </div>

          {/* AI Summary */}
          {response.ai_summary && (
            <div className="card bg-violet/5 border-violet/20">
              <p className="text-xs text-violet mb-2">✦ {t('ai.summary')}</p>
              <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">{response.ai_summary}</p>
            </div>
          )}

          {/* Results */}
          <div>
            <p className="text-sm text-muted mb-3">
              {t('ai.productsFound', { count: new Intl.NumberFormat(locale).format(response.products.length) })}
            </p>
            {response.products.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {response.products.map((item: MeliItem) => (
                  <ProductCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <div className="card text-center py-10">
                <p className="text-muted">{t('ai.none')}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  )
}
