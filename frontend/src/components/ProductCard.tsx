import type { MeliItem, OfferWithDeal } from '../types'
import { formatCurrency, classifyColor, classifyLabel, truncate } from '../utils/format'

interface ProductCardProps {
  item?: MeliItem
  offer?: OfferWithDeal
}

export default function ProductCard({ item, offer }: ProductCardProps) {
  if (item) {
    return <MeliCard item={item} />
  }
  if (offer) {
    return <OfferCard offer={offer} />
  }
  return null
}

function MeliCard({ item }: { item: MeliItem }) {
  const discount =
    item.original_price && item.original_price > item.price
      ? Math.round(((item.original_price - item.price) / item.original_price) * 100)
      : null

  return (
    <a
      href={item.permalink}
      target="_blank"
      rel="noopener noreferrer"
      className="card flex flex-col gap-3 hover:border-accent/50 transition-colors group"
    >
      <div className="aspect-square bg-background rounded-lg overflow-hidden flex items-center justify-center">
        <img
          src={item.thumbnail}
          alt={item.title}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform"
          onError={e => { (e.target as HTMLImageElement).src = '/placeholder.svg' }}
        />
      </div>
      <div className="flex flex-col gap-1 flex-1">
        <p className="text-sm text-white leading-snug">{truncate(item.title, 70)}</p>
        <p className="text-xs text-muted">{item.condition === 'new' ? 'Novo' : 'Usado'}</p>
      </div>
      <div className="flex items-end justify-between gap-2">
        <div>
          {item.original_price && item.original_price > item.price && (
            <p className="text-xs text-muted line-through">{formatCurrency(item.original_price)}</p>
          )}
          <p className="text-lg font-bold text-white">{formatCurrency(item.price)}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          {discount && (
            <span className="badge text-success bg-success/10">-{discount}%</span>
          )}
          {item.shipping.free_shipping && (
            <span className="text-xs text-success">Frete grátis</span>
          )}
        </div>
      </div>
    </a>
  )
}

function OfferCard({ offer }: { offer: OfferWithDeal }) {
  const labelColor = classifyColor(offer.deal_classification)
  const label = classifyLabel(offer.deal_classification)

  return (
    <a
      href={offer.product_url}
      target="_blank"
      rel="noopener noreferrer"
      className="card flex flex-col gap-3 hover:border-accent/50 transition-colors"
    >
      <div className="flex flex-col gap-1 flex-1">
        <span className={`badge self-start ${labelColor}`}>{label}</span>
        <p className="text-sm text-muted">
          {offer.condition === 'new' ? 'Novo' : 'Usado'} ·{' '}
          {offer.seller_name ?? 'Vendedor'}
          {offer.free_shipping && <span className="text-success"> · Frete grátis</span>}
        </p>
      </div>
      <div className="flex items-end justify-between">
        <div>
          {offer.original_price && offer.original_price > offer.current_price && (
            <p className="text-xs text-muted line-through">{formatCurrency(Number(offer.original_price))}</p>
          )}
          <p className="text-xl font-bold text-white">{formatCurrency(Number(offer.current_price))}</p>
        </div>
        {offer.discount_percent && (
          <span className="badge text-success bg-success/10">-{Number(offer.discount_percent).toFixed(0)}%</span>
        )}
      </div>
      {offer.history_points > 0 && (
        <p className="text-xs text-muted">{offer.history_points} pontos de histórico</p>
      )}
    </a>
  )
}
