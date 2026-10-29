// Service layer — typed wrappers around the backend API.
import api from './api'
import type {
  User, Token, Product, Offer, OfferWithDeal, PriceAlert, Notification,
  Favorite, PaginatedResponse, MeliItem, AISearchResponse,
} from '../types'

// ── Auth ──────────────────────────────────────────────────────────────────
export const authService = {
  register: (name: string, email: string, password: string) =>
    api.post<User>('/auth/register', { name, email, password }),

  login: async (email: string, password: string): Promise<Token> => {
    const form = new URLSearchParams({ username: email, password })
    const { data } = await api.post<Token>('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },

  refresh: (refresh_token: string) =>
    api.post<Token>('/auth/refresh', { refresh_token }),

  logout: (refresh_token: string) =>
    api.post('/auth/logout', { refresh_token }),
}

// ── Users ─────────────────────────────────────────────────────────────────
export const userService = {
  getMe: () => api.get<User>('/users/me'),
  getAlerts: () => api.get<PriceAlert[]>('/users/me/alerts'),
  createAlert: (product_id: string, target_price: number) =>
    api.post<PriceAlert>('/users/me/alerts', { product_id, target_price }),
  deleteAlert: (alert_id: string) =>
    api.delete(`/users/me/alerts/${alert_id}`),
  getNotifications: () => api.get<Notification[]>('/users/me/notifications'),
}

// ── Products ──────────────────────────────────────────────────────────────
export const productService = {
  searchLocal: (params: Record<string, unknown>) =>
    api.get<PaginatedResponse<Product>>('/products/search', { params }),

  searchLive: (params: Record<string, unknown>) =>
    api.get<{ query: string; total: number; offset: number; limit: number; results: MeliItem[] }>(
      '/products/search/live', { params }),

  getProduct: (id: string) => api.get<Product>(`/products/${id}`),

  getOffers: (product_id: string) =>
    api.get<Offer[]>(`/products/${product_id}/offers`),

  addFavorite: (product_id: string) =>
    api.post<Favorite>(`/products/${product_id}/favorite`),

  removeFavorite: (product_id: string) =>
    api.delete(`/products/${product_id}/favorite`),

  getFavorites: () => api.get<Favorite[]>('/products/favorites/me'),
}

// ── Deals ─────────────────────────────────────────────────────────────────
export const dealsService = {
  getDeals: (params?: { category_id?: string; limit?: number }) =>
    api.get<OfferWithDeal[]>('/deals', { params }),
}

// ── Categories ───────────────────────────────────────────────────────────
export const categoryService = {
  getCategories: () => api.get<{ id: string; name: string; slug: string }[]>('/categories'),
}

// ── AI ───────────────────────────────────────────────────────────────────
export const aiService = {
  search: (query: string, page = 1, limit = 20) =>
    api.post<AISearchResponse>('/ai/search', { query, page, limit }),

  analyzeOffer: (offer_id: string) =>
    api.get(`/ai/analyze/${offer_id}`),
}

// ── Admin ─────────────────────────────────────────────────────────────────
export const adminService = {
  getStats: () => api.get<{ users: number; products: number; alerts: number }>('/admin/stats'),
  getUsers: () => api.get<User[]>('/admin/users'),
  deactivateUser: (id: string) => api.patch(`/admin/users/${id}/deactivate`),
  activateUser: (id: string) => api.patch(`/admin/users/${id}/activate`),
  getCollectionSources: () => api.get('/admin/collection-sources'),
  getCollectionRuns: () => api.get('/admin/collection-runs'),
}
