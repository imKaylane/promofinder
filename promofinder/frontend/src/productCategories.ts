import type { TranslationKey } from './i18n'

export const productCategories = [
  { slug: 'pc', label: 'home.categoryPC', icon: '▦', color: 'from-blue-500/20 to-cyan-400/10' },
  { slug: 'peripherals', label: 'home.categoryPeripherals', icon: '⌨', color: 'from-violet-500/20 to-indigo-400/10' },
] as const satisfies readonly {
  slug: string
  label: TranslationKey
  icon: string
  color: string
}[]

export type ProductCategorySlug = typeof productCategories[number]['slug']
