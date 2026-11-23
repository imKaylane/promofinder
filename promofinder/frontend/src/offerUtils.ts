import type { OfferWithDeal } from './types'

export function deduplicateOffers(offers: OfferWithDeal[]): OfferWithDeal[] {
  const bestOffers = new Map<string, OfferWithDeal>()
  for (const offer of offers) {
    const previous = bestOffers.get(offer.product_url)
    if (!previous || Number(offer.current_price) < Number(previous.current_price)) {
      bestOffers.set(offer.product_url, offer)
    }
  }
  return Array.from(bestOffers.values())
}
