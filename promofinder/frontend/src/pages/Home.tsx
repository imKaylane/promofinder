import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { dealsService, productService } from '../services'
import ProductCard from '../components/ProductCard'
import type { Favorite, OfferWithDeal } from '../types'
import { useLanguage } from '../i18n'
import { productCategories } from '../productCategories'
import { deduplicateOffers } from '../offerUtils'

export default function Home() {
  const { t, locale } = useLanguage()
  const { isAuthenticated } = useAuth()
  const [deals, setDeals] = useState<OfferWithDeal[]>([])
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [favoriteLoadError, setFavoriteLoadError] = useState('')
  const [featuredIndex, setFeaturedIndex] = useState(0)

  const loadDeals = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await dealsService.getDeals({ limit: 12 })
      setDeals(deduplicateOffers(data))
      setFeaturedIndex(0)
    } catch {
      setError(t('home.error'))
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    void loadDeals()
  }, [loadDeals])

  useEffect(() => {
    if (!isAuthenticated) {
      setFavoriteIds(new Set())
      setFavoriteLoadError('')
      return
    }

    productService.getFavorites()
      .then(({ data }: { data: Favorite[] }) => {
        setFavoriteIds(new Set(data.map(favorite => favorite.product_id)))
        setFavoriteLoadError('')
      })
      .catch(() => setFavoriteLoadError(t('home.favoriteError')))
  }, [isAuthenticated, t])

  const featuredDeals = deals.slice(0, 4)
  const featured = featuredDeals[featuredIndex]

  const showPrevious = () => {
    setFeaturedIndex(index => (index - 1 + featuredDeals.length) % featuredDeals.length)
  }
  const showNext = () => {
    setFeaturedIndex(index => (index + 1) % featuredDeals.length)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-10 px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
      <section aria-label={t('home.featuredSection')}>
        {loading ? (
          <div className="h-64 animate-pulse rounded-3xl bg-border sm:h-72" />
        ) : featured ? (
          <div className="promo-banner relative isolate min-h-64 overflow-hidden rounded-3xl bg-gradient-to-br from-neutral-950 via-neutral-900 to-emerald-950 p-6 text-white sm:min-h-72 sm:p-10">
            {featured.product?.image_url && (
              <img
                src={featured.product.image_url}
                alt=""
                className="pointer-events-none absolute -right-8 -top-8 -z-10 h-[115%] w-2/3 object-contain opacity-20 sm:right-6 sm:top-0 sm:h-full sm:w-1/2 sm:opacity-30"
                onError={event => { event.currentTarget.style.display = 'none' }}
              />
            )}
            <div className="max-w-2xl">
              <span className="inline-flex items-center gap-2 rounded-md border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-emerald-100">
                <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                {t('home.featuredLabel')}
              </span>
              <p className="mt-5 text-sm font-medium text-emerald-200">
                {featured.product?.name ?? t('home.featuredFallback')}
              </p>
              <h1 className="mt-2 max-w-xl text-3xl font-bold leading-tight sm:text-4xl">
                {t('home.headline')}
              </h1>
              <div className="mt-4 flex flex-wrap items-baseline gap-x-3 gap-y-1">
                <span className="text-3xl font-bold">{formatDealPrice(featured.current_price, locale)}</span>
                {featured.original_price && Number(featured.original_price) > Number(featured.current_price) && (
                  <span className="text-base text-emerald-200/70 line-through">
                    {formatDealPrice(featured.original_price, locale)}
                  </span>
                )}
              </div>
              <div className="mt-6 flex flex-wrap items-center gap-3">
                <a
                  href={featured.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-[#06150e] transition hover:brightness-110"
                >
                  {t('home.buy')} <span aria-hidden="true">↗</span>
                </a>
                <Link to="/deals" className="rounded-lg border border-white/20 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10">
                  {t('home.explore')}
                </Link>
              </div>
              <p className="mt-5 text-xs text-emerald-100/80">{t('home.updatedRegularly')}</p>
            </div>
            {featuredDeals.length > 1 && (
              <div className="absolute bottom-5 right-5 flex items-center gap-2 sm:bottom-8 sm:right-8">
                <button
                  type="button"
                  onClick={showPrevious}
                  className="grid h-9 w-9 place-items-center rounded-lg border border-white/20 bg-white/10 transition hover:bg-white/20"
                  aria-label={t('home.previous')}
                >
                  ←
                </button>
                <div className="flex items-center gap-1.5" aria-label={t('home.featuredPosition', { current: featuredIndex + 1, total: featuredDeals.length })}>
                  {featuredDeals.map((deal, index) => (
                    <button
                      key={deal.id}
                      type="button"
                      onClick={() => setFeaturedIndex(index)}
                      aria-label={t('home.showHighlight', { number: index + 1 })}
                      aria-current={featuredIndex === index}
                      className={`h-2 rounded-full transition-all ${featuredIndex === index ? 'w-6 bg-white' : 'w-2 bg-white/40'}`}
                    />
                  ))}
                </div>
                <button
                  type="button"
                  onClick={showNext}
                  className="grid h-9 w-9 place-items-center rounded-lg border border-white/20 bg-white/10 transition hover:bg-white/20"
                  aria-label={t('home.next')}
                >
                  →
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="promo-banner rounded-3xl bg-gradient-to-br from-neutral-950 via-neutral-900 to-emerald-950 px-6 py-10 text-white sm:px-10">
            <span className="text-xs font-semibold tracking-widest text-emerald-200">PROMOFINDER</span>
            <h1 className="mt-3 max-w-xl text-3xl font-bold sm:text-4xl">{t('home.defaultHeadline')}</h1>
            <p className="mt-3 max-w-lg text-sm text-emerald-100/80">
              {t('home.defaultDescription')}
            </p>
            <Link to="/search" className="mt-6 inline-flex rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-[#06150e]">
              {t('home.searchProducts')} <span className="ml-2" aria-hidden="true">↗</span>
            </Link>
          </div>
        )}
      </section>

      <section aria-labelledby="categories-heading">
        <div className="mb-4 flex items-end justify-between">
          <div>
            <p className="text-sm font-medium text-accent">{t('home.find')}</p>
            <h2 id="categories-heading" className="mt-1 text-xl font-bold">{t('home.exploreCategories')}</h2>
          </div>
        </div>
        <div className="grid max-w-2xl grid-cols-2 gap-3">
          {productCategories.map(category => (
            <Link
              key={category.slug}
              to={`/categories/${category.slug}`}
              className={`group flex min-h-32 flex-col items-center justify-center gap-3 rounded-xl border border-border bg-gradient-to-br ${category.color} p-4 transition hover:-translate-y-0.5 hover:border-accent/50`}
            >
              <span className="grid h-12 w-12 place-items-center rounded-lg bg-surface/80 text-2xl text-accent transition group-hover:scale-105">
                {category.icon}
              </span>
              <span className="text-sm font-semibold">{t(category.label)}</span>
            </Link>
          ))}
        </div>
      </section>

      <section aria-labelledby="deals-heading">
        <div className="mb-5 flex items-end justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-accent">{t('home.selectedForYou')}</p>
            <h2 id="deals-heading" className="mt-1 text-xl font-bold sm:text-2xl">{t('home.featuredDeals')}</h2>
          </div>
          <Link to="/deals" className="shrink-0 text-sm font-medium text-accent hover:underline">
            {t('home.viewAll')} <span aria-hidden="true">→</span>
          </Link>
        </div>

        {favoriteLoadError && (
          <p role="status" className="mb-4 rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning">
            {favoriteLoadError} {t('home.favoriteWarning')}
          </p>
        )}

        {error ? (
          <div role="alert" className="card py-12 text-center">
            <p className="font-medium">{error}</p>
            <button type="button" onClick={() => void loadDeals()} className="btn-primary mt-4">
              {t('home.tryAgain')}
            </button>
          </div>
        ) : loading ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="card animate-pulse space-y-3">
                <div className="aspect-square rounded-lg bg-border" />
                <div className="h-4 w-4/5 rounded bg-border" />
                <div className="h-3 w-2/5 rounded bg-border" />
                <div className="h-9 rounded-lg bg-border" />
              </div>
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="card py-12 text-center">
            <p className="font-medium">{t('home.emptyTitle')}</p>
            <p className="mt-2 text-sm text-muted">{t('home.emptyText')}</p>
            <Link to="/search" className="btn-primary mt-5 inline-flex">{t('home.searchProducts')}</Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
            {deals.map(offer => (
              <ProductCard
                key={offer.id}
                offer={offer}
                isFavorite={favoriteIds.has(offer.product_id)}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

function formatDealPrice(price: number | string, locale: string) {
  return new Intl.NumberFormat(locale, { style: 'currency', currency: 'BRL' }).format(Number(price))
}
