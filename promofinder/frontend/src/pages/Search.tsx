import { useCallback, useEffect, useRef, useState, FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { productService } from '../services'
import ProductCard from '../components/ProductCard'
import type { MeliItem } from '../types'
import { useLanguage } from '../i18n'

type LiveSearchParams = {
  q: string
  min_price?: string
  max_price?: string
  condition?: string
  sort: string
}

const focusSearches = [
  { label: 'search.categoryPC', query: 'placa de video' },
  { label: 'search.categoryPeripherals', query: 'perifericos gamer' },
] as const

export default function Search() {
  const { t, locale } = useLanguage()
  const [searchParams] = useSearchParams()
  const activeSearch = useRef<LiveSearchParams | null>(null)
  const [query, setQuery] = useState(searchParams.get('q') ?? '')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [condition, setCondition] = useState('')
  const [sort, setSort] = useState('relevance')
  const [results, setResults] = useState<MeliItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const runSearch = useCallback(async (
    searchQuery: string,
    offset = 0,
    append = false,
  ) => {
    if (!searchQuery.trim()) return
    setLoading(true)
    setError('')
    try {
      const params = append && activeSearch.current
        ? activeSearch.current
        : {
            q: searchQuery,
            min_price: minPrice || undefined,
            max_price: maxPrice || undefined,
            condition: condition || undefined,
            sort,
          }
      if (!append) activeSearch.current = params
      const { data } = await productService.searchLive({
        ...params,
        limit: 24,
        offset,
      })
      setResults(current => append ? [...current, ...data.results] : data.results)
      setTotal(data.total)
      setSearched(true)
    } catch {
      setError(t('search.error'))
    } finally {
      setLoading(false)
    }
  }, [condition, maxPrice, minPrice, sort, t])

  useEffect(() => {
    const urlQuery = searchParams.get('q')
    if (urlQuery?.trim()) {
      setQuery(urlQuery)
      void runSearch(urlQuery)
    }
  }, [runSearch, searchParams])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    void runSearch(query)
  }

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-foreground">{t('search.title')}</h1>

      <form onSubmit={handleSubmit} className="card mb-6 flex flex-col gap-4">
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            className="input flex-1"
            placeholder={t('search.example')}
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <button type="submit" className="btn-primary px-6 sm:w-auto" disabled={loading}>
            {loading ? t('search.loading') : t('search.submit')}
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted">{t('search.explore')}</span>
          {focusSearches.map(search => (
            <button
              key={search.query}
              type="button"
              className="rounded-md border border-border px-3 py-1 text-sm text-muted transition hover:border-accent hover:text-accent"
              onClick={() => {
                setQuery(search.query)
                void runSearch(search.query)
              }}
            >
              {t(search.label)}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <input
            className="input"
            aria-label={t('search.minPrice')}
            placeholder={t('search.minPrice')}
            type="number"
            min={0}
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
          />
          <input
            className="input"
            aria-label={t('search.maxPrice')}
            placeholder={t('search.maxPrice')}
            type="number"
            min={0}
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
          />
          <select className="input" aria-label={t('search.condition')} value={condition} onChange={e => setCondition(e.target.value)}>
            <option value="">{t('search.allConditions')}</option>
            <option value="new">{t('search.new')}</option>
            <option value="used">{t('search.used')}</option>
          </select>
          <select className="input" aria-label={t('search.sort')} value={sort} onChange={e => setSort(e.target.value)}>
            <option value="relevance">{t('search.relevance')}</option>
            <option value="price_asc">{t('search.lowestPrice')}</option>
            <option value="price_desc">{t('search.highestPrice')}</option>
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
          {t(total === 1 ? 'search.oneResult' : 'search.results', {
            count: new Intl.NumberFormat(locale).format(total),
            query,
          })}
        </p>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {results.map(item => (
            <ProductCard key={item.id} item={item} />
          ))}
        </div>
      )}

      {results.length > 0 && results.length < total && (
        <div className="mt-8 flex justify-center">
          <button
            type="button"
            className="btn-primary px-6"
            disabled={loading}
            onClick={() => void runSearch(activeSearch.current?.q ?? query, results.length, true)}
          >
            {loading ? t('search.loading') : t('search.loadMore')}
          </button>
        </div>
      )}

      {searched && results.length === 0 && !loading && (
        <div className="card text-center py-12">
          <p className="text-muted">{t('search.none')}</p>
          <p className="text-sm text-muted mt-1">{t('search.tryAgain')}</p>
        </div>
      )}
    </main>
  )
}
