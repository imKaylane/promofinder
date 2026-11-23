import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { useLanguage } from '../i18n'
import { productCategories } from '../productCategories'
import { dealsService } from '../services'
import type { OfferWithDeal } from '../types'
import { deduplicateOffers } from '../offerUtils'

export default function CategoryDeals() {
  const { slug } = useParams()
  const { t, locale } = useLanguage()
  const category = productCategories.find(item => item.slug === slug)
  const [deals, setDeals] = useState<OfferWithDeal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDeals = useCallback(async () => {
    if (!category) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')
    try {
      const { data } = await dealsService.getDeals({ category: category.slug, limit: 50 })
      setDeals(deduplicateOffers(data.filter(isPromotion)))
    } catch {
      setError(t('deals.error'))
    } finally {
      setLoading(false)
    }
  }, [category, t])

  useEffect(() => {
    void loadDeals()
  }, [loadDeals])

  if (!category) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-8">
        <h1 className="text-2xl font-bold">{t('error.notFoundTitle')}</h1>
      </main>
    )
  }

  function isPromotion(offer: OfferWithDeal) {
    return (
      ['price_below_history', 'price_drop_detected', 'potential_deal'].includes(offer.deal_classification)
      || Number(offer.original_price) > Number(offer.current_price)
    )
  }

  const categoryName = t(category.label)

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6">
        <Link to="/" className="text-sm font-medium text-accent hover:underline">
          ← {t('nav.home')}
        </Link>
        <h1 className="mt-3 text-2xl font-bold text-foreground">
          {t('deals.categoryTitle', { category: categoryName })}
        </h1>
        <p className="mt-1 text-sm text-muted">{t('deals.categoryDescription')}</p>
      </div>

      {error && (
        <div role="alert" className="card mb-4 border-danger/30 text-danger">
          <p>{error}</p>
          <button type="button" onClick={() => void loadDeals()} className="btn-primary mt-3">
            {t('home.tryAgain')}
          </button>
        </div>
      )}

      {!error && loading ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="card h-40 animate-pulse bg-border" />
          ))}
        </div>
      ) : !error && deals.length === 0 ? (
        <div className="card py-16 text-center">
          <p className="text-lg font-medium">{t('deals.categoryNone', { category: categoryName })}</p>
          <p className="mt-2 text-sm text-muted">{t('deals.categoryNoneText')}</p>
        </div>
      ) : !error ? (
        <>
          <p className="mb-4 text-sm text-muted">
            {t('deals.items', { count: new Intl.NumberFormat(locale).format(deals.length) })}
          </p>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {deals.map(offer => <ProductCard key={offer.id} offer={offer} />)}
          </div>
        </>
      ) : null}
    </main>
  )
}
