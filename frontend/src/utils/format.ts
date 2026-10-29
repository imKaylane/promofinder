// Utility functions for formatting values in the UI.

export function formatCurrency(value: number, currency = 'BRL'): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(value)
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso))
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat('pt-BR').format(n)
}

export function classifyColor(classification: string): string {
  const map: Record<string, string> = {
    price_below_history: 'text-success bg-success/10',
    price_drop_detected: 'text-accent bg-accent/10',
    potential_deal: 'text-warning bg-warning/10',
    regular_price: 'text-muted bg-white/5',
    insufficient_history: 'text-muted bg-white/5',
    outdated_data: 'text-danger bg-danger/10',
  }
  return map[classification] ?? 'text-muted bg-white/5'
}

export function classifyLabel(classification: string): string {
  const map: Record<string, string> = {
    price_below_history: '🔥 Menor preço histórico',
    price_drop_detected: '📉 Queda detectada',
    potential_deal: '⚡ Promoção potencial',
    regular_price: 'Preço normal',
    insufficient_history: 'Histórico insuficiente',
    outdated_data: 'Dados desatualizados',
  }
  return map[classification] ?? classification
}

export function truncate(text: string, max = 80): string {
  return text.length > max ? text.slice(0, max) + '…' : text
}
