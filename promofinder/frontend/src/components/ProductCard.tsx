import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { productService } from '../services'
import type { MeliItem, OfferWithDeal } from '../types'
import { formatCurrency, classifyColor, classifyLabel, truncate } from '../utils/format'
import { useLanguage } from '../i18n'

interface ProductCardProps {
  item?: MeliItem
  offer?: OfferWithDeal
  isFavorite?: boolean
}

export default function ProductCard({ item, offer, isFavorite = false }: ProductCardProps) {
  if (item) return <MeliCard item={item} />
  if (offer) return <OfferCard offer={offer} isFavorite={isFavorite} />
  return null
}

function MeliCard({ item }: { item: MeliItem }) {
  const { t, locale } = useLanguage()
  const discount = item.original_price && item.original_price > item.price
    ? Math.round(((item.original_price - item.price) / item.original_price) * 100)
    : null

  return (
    <article className="card group flex flex-col gap-3 transition-all hover:-translate-y-0.5 hover:border-accent/50">
      <a
        href={item.permalink}
        target="_blank"
        rel="noopener noreferrer"
        className="flex flex-1 flex-col gap-3"
      >
        <div className="aspect-square overflow-hidden rounded-lg bg-background">
          <img
            src={item.thumbnail}
            alt={item.title}
            className="h-full w-full object-contain transition-transform duration-300 group-hover:scale-105"
            onError={event => { event.currentTarget.src = '/placeholder.svg' }}
          />
        </div>
        <div className="flex flex-1 flex-col gap-1">
          <p className="line-clamp-2 text-sm leading-snug">{truncate(item.title, 90)}</p>
          <p className="text-xs text-muted">Mercado Livre · {t(item.condition === 'new' ? 'product.new' : 'product.used')}</p>
        </div>
        <div className="flex items-end justify-between gap-2">
          <div>
            {item.original_price && item.original_price > item.price && (
              <p className="text-xs text-muted line-through">{formatCurrency(item.original_price, 'BRL', locale)}</p>
            )}
            <p className="text-lg font-bold">{formatCurrency(item.price, 'BRL', locale)}</p>
          </div>
          {discount && <span className="badge bg-success/10 text-success">-{discount}%</span>}
        </div>
      </a>
      <a
        href={item.permalink}
        target="_blank"
        rel="noopener noreferrer"
        className="btn-primary flex items-center justify-center gap-2 text-sm"
      >
        {t('product.viewOffer')} <span aria-hidden="true">↗</span>
      </a>
    </article>
  )
}

function OfferCard({ offer, isFavorite }: { offer: OfferWithDeal; isFavorite: boolean }) {
  const { t, locale } = useLanguage()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [favorite, setFavorite] = useState(isFavorite)
  const [savingFavorite, setSavingFavorite] = useState(false)
  const [favoriteError, setFavoriteError] = useState('')
  const product = offer.product
  const analyzedDiscount = Number(offer.discount_percent)
  const originalPrice = Number(offer.original_price)
  const currentPrice = Number(offer.current_price)
  const discount = Number.isFinite(analyzedDiscount) && analyzedDiscount > 0
    ? analyzedDiscount
    : originalPrice > currentPrice
      ? Math.round(((originalPrice - currentPrice) / originalPrice) * 100)
      : 0
  const hasDiscount = discount > 0
  const dealClassification = hasDiscount && offer.deal_classification === 'regular_price'
    ? 'price_drop_detected'
    : offer.deal_classification
  const classification = classifyColor(dealClassification)

  useEffect(() => {
    setFavorite(isFavorite)
  }, [isFavorite])

  const toggleFavorite = async () => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    setSavingFavorite(true)
    setFavoriteError('')
    try {
      if (favorite) {
        await productService.removeFavorite(offer.product_id)
        setFavorite(false)
      } else {
        await productService.addFavorite(offer.product_id)
        setFavorite(true)
      }
    } catch {
      setFavoriteError(t('product.favoriteError'))
    } finally {
      setSavingFavorite(false)
    }
  }

  return (
    <article className="card group flex flex-col gap-3 transition-all hover:-translate-y-0.5 hover:border-accent/50">
      <div className="relative">
        <a
          href={offer.product_url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`${t('product.viewOffer')}: ${product?.name ?? t('deals.title')}`}
          className="block aspect-square overflow-hidden rounded-lg bg-background"
        >
          {product?.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="h-full w-full object-contain transition-transform duration-300 group-hover:scale-105"
              onError={event => { event.currentTarget.style.display = 'none' }}
            />
          ) : (
            <div className="grid h-full place-items-center bg-gradient-to-br from-accent/10 via-surface to-violet/10 text-5xl" aria-hidden="true">
              ✨
            </div>
          )}
        </a>
        {hasDiscount && (
          <span className="absolute left-2 top-2 badge bg-accent text-[#06150e]">-{discount.toFixed(0)}%</span>
        )}
        <button
          type="button"
          onClick={toggleFavorite}
          disabled={savingFavorite}
          aria-label={favorite ? t('product.favoriteRemove') : t('product.favoriteAdd')}
          aria-pressed={favorite}
          title={favorite ? t('product.favoriteRemove') : t('product.favoriteAdd')}
          className={`absolute right-2 top-2 grid h-9 w-9 place-items-center rounded-full border border-border bg-surface/90 text-xl shadow-sm transition-colors hover:text-danger disabled:opacity-50 ${
            favorite ? 'text-danger' : 'text-muted'
          }`}
        >
          {favorite ? '♥' : '♡'}
        </button>
      </div>

      <div className="flex flex-1 flex-col gap-1">
        <p className="line-clamp-2 min-h-10 text-sm leading-snug">
          {product?.name ?? `Oferta ${offer.external_id}`}
        </p>
        <p className="text-xs text-muted">
          {offer.source === 'mercadolivre' ? 'Mercado Livre' : offer.source}
          {offer.seller_name ? ` · ${offer.seller_name}` : ''}
        </p>
        <span className={`badge mt-1 self-start ${classification}`}>
          {t(classifyLabel(dealClassification))}
        </span>
      </div>

      <div className="flex items-end justify-between gap-2">
        <div>
          {offer.original_price && Number(offer.original_price) > Number(offer.current_price) && (
            <p className="text-xs text-muted line-through">{formatCurrency(Number(offer.original_price), 'BRL', locale)}</p>
          )}
          <p className="text-lg font-bold">{formatCurrency(Number(offer.current_price), 'BRL', locale)}</p>
        </div>
        {offer.free_shipping && <span className="text-right text-xs text-success">{t('product.freeShipping')}</span>}
      </div>

      {favoriteError && <p role="status" className="text-xs text-danger">{favoriteError}</p>}

      <a
        href={offer.product_url}
        target="_blank"
        rel="noopener noreferrer"
        className="btn-primary flex items-center justify-center gap-2 text-sm"
      >
        {t('product.viewOffer')} <span aria-hidden="true">↗</span>
      </a>
    </article>
  )
}
