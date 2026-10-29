// Shared TypeScript types for the TechDeals AI frontend.

export interface User {
  id: string
  name: string
  email: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Category {
  id: string
  name: string
  slug: string
  description?: string
}

export interface Product {
  id: string
  name: string
  brand?: string
  model?: string
  description?: string
  category_id?: string
  image_url?: string
  specifications?: string
  created_at: string
  updated_at: string
}

export interface Offer {
  id: string
  product_id: string
  source: string
  external_id: string
  product_url: string
  current_price: number
  original_price?: number
  currency: string
  availability_status: string
  condition: string
  free_shipping: boolean
  seller_name?: string
  seller_reputation?: string
  last_checked_at: string
}

export interface OfferWithDeal extends Offer {
  discount_percent?: number
  deal_classification: string
  history_points: number
  min_price_observed?: number
  price_trend?: string
}

export interface PriceAlert {
  id: string
  product_id: string
  target_price: number
  is_active: boolean
  created_at: string
  updated_at: string
  product?: Product
}

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  related_product_id?: string
  read_at?: string
  created_at: string
}

export interface Favorite {
  id: string
  product_id: string
  created_at: string
  product?: Product
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}

// Raw Mercado Livre item (from /search/live)
export interface MeliItem {
  id: string
  title: string
  price: number
  original_price?: number
  currency_id: string
  thumbnail: string
  permalink: string
  condition: string
  available_quantity: number
  sold_quantity: number
  shipping: { free_shipping: boolean }
  seller: { id: number; nickname: string }
}

export interface AISearchResponse {
  interpreted_query: string
  filters_extracted: Record<string, unknown>
  products: MeliItem[]
  ai_summary?: string
  ai_available: boolean
}

export type DealClassification =
  | 'price_below_history'
  | 'price_drop_detected'
  | 'potential_deal'
  | 'regular_price'
  | 'insufficient_history'
  | 'outdated_data'
