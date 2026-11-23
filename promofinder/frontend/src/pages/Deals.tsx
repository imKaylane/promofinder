import { useState, useEffect } from 'react'
import { dealsService } from '../services'
import ProductCard from '../components/ProductCard'
import type { OfferWithDeal } from '../types'
import { useLanguage } from '../i18n'
import { deduplicateOffers } from '../offerUtils'

export default function Deals() {
  const { t } = useLanguage()
  const [deals, setDeals] = useState<OfferWithDeal[]>([])
  const [loading, setLoading] = useState(true)
  const [limit, setLimit] = useState(20)

  const load = async (l = limit) => {
    setLoading(true)
    try {
      const { data } = await dealsService.getDeals({ limit: l })
      setDeals(deduplicateOffers(data))
    } catch {
      setDeals([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">🔥 {t('deals.title')}</h1>
          <p className="mt-1 text-sm text-muted">{t('deals.description')}</p>
        </div>
        <select
          className="input w-full sm:w-auto"
          aria-label={t('deals.title')}
          value={limit}
          onChange={e => { setLimit(Number(e.target.value)); load(Number(e.target.value)) }}
        >
          <option value={10}>{t('deals.items', { count: 10 })}</option>
          <option value={20}>{t('deals.items', { count: 20 })}</option>
          <option value={50}>{t('deals.items', { count: 50 })}</option>
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
          <p className="text-lg text-muted">{t('deals.none')}</p>
          <p className="text-sm text-muted mt-2">
            {t('deals.noneText')}
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
