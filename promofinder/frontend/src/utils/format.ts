// Utility functions for formatting values in the UI.
import type { TranslationKey } from '../i18n'

export function formatCurrency(value: number, currency = 'BRL', locale = 'pt-BR'): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(value)
}

export function formatDate(iso: string, locale = 'pt-BR'): string {
  return new Intl.DateTimeFormat(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso))
}

export function formatNumber(n: number, locale = 'pt-BR'): string {
  return new Intl.NumberFormat(locale).format(n)
}

export function classifyColor(classification: string): string {
  const map: Record<string, string> = {
    price_below_history: 'text-success bg-success/10',
    price_drop_detected: 'text-accent bg-accent/10',
    potential_deal: 'text-warning bg-warning/10',
    regular_price: 'text-muted bg-background',
    insufficient_history: 'text-muted bg-background',
    outdated_data: 'text-danger bg-danger/10',
  }
  return map[classification] ?? 'text-muted bg-white/5'
}

export function classifyLabel(classification: string): TranslationKey {
  const map: Record<string, TranslationKey> = {
    price_below_history: 'deal.lowestHistory',
    price_drop_detected: 'deal.priceDrop',
    potential_deal: 'deal.potential',
    regular_price: 'deal.regular',
    insufficient_history: 'deal.insufficientHistory',
    outdated_data: 'deal.outdated',
  }
  return map[classification] ?? 'deal.regular'
}

export function truncate(text: string, max = 80): string {
  return text.length > max ? text.slice(0, max) + '…' : text
}
