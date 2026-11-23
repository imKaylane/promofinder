import { FormEvent, ReactNode, useEffect, useState } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n'
import LanguageSelect from './LanguageSelect'
import ThemeToggle from './ThemeToggle'

interface NavigationItem {
  label: 'nav.home' | 'nav.search' | 'nav.alerts' | 'nav.favorites' | 'nav.profile' | 'nav.deals' | 'nav.aiSearch' | 'nav.admin'
  shortLabel?: 'nav.searchShort' | 'nav.alertsShort' | 'nav.profileShort'
  to: string
  icon: string
}

const navigationItems = [
  { label: 'nav.home', to: '/', icon: '⌂' },
  { label: 'nav.search', shortLabel: 'nav.searchShort', to: '/search', icon: '⌕' },
  { label: 'nav.alerts', shortLabel: 'nav.alertsShort', to: '/alerts', icon: '♧' },
  { label: 'nav.favorites', to: '/favorites', icon: '♡' },
  { label: 'nav.profile', shortLabel: 'nav.profileShort', to: '/profile', icon: '◎' },
] satisfies readonly NavigationItem[]

const secondaryItems = [
  { label: 'nav.deals', to: '/deals', icon: '↗' },
  { label: 'nav.aiSearch', to: '/ai-search', icon: '✦' },
] satisfies readonly NavigationItem[]

interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const { user, isAuthenticated, logout } = useAuth()
  const { t } = useLanguage()
  const location = useLocation()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [profileMenuOpen, setProfileMenuOpen] = useState(false)
  const [quickSearch, setQuickSearch] = useState('')
  useEffect(() => {
    setMobileMenuOpen(false)
    setProfileMenuOpen(false)
  }, [location.pathname])

  const handleQuickSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const query = quickSearch.trim()
    if (query) navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const renderLinks = (items: readonly NavigationItem[]) =>
    items.map(item => (
      <NavLink
        key={item.to}
        to={item.to}
        end={item.to === '/'}
        className={({ isActive }) =>
          `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors ${
            isActive
              ? 'bg-accent/10 font-semibold text-accent'
              : 'text-muted hover:bg-background hover:text-foreground'
          }`
        }
      >
        <span className="w-5 text-center text-lg leading-none" aria-hidden="true">{item.icon}</span>
        <span>{t(item.label)}</span>
      </NavLink>
    ))

  const sidebar = (
    <div className="flex h-full flex-col">
      <Link to="/" className="flex h-16 items-center gap-3 border-b border-border px-6">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-accent text-lg text-[#06150e]">⚡</span>
        <span className="text-lg font-bold tracking-tight">promoFinder</span>
      </Link>
      <nav aria-label={t('nav.primary')} className="flex-1 space-y-1 px-3 py-6">
        <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-muted">{t('nav.menu')}</p>
        {renderLinks(navigationItems)}
        <p className="px-3 pb-2 pt-7 text-xs font-semibold uppercase tracking-wider text-muted">{t('nav.discover')}</p>
        {renderLinks(secondaryItems)}
        {user?.role === 'admin' && renderLinks([{ label: 'nav.admin', to: '/admin', icon: '⚙' }])}
      </nav>
      <div className="border-t border-border p-4">
        <div className="rounded-xl bg-background p-3">
          <p className="text-sm font-semibold">{t('shell.footerTitle')}</p>
          <p className="mt-1 text-xs text-muted">{t('shell.footerText')}</p>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-background text-current">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-border bg-surface md:block">
        {sidebar}
      </aside>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            className="absolute inset-0 h-full w-full bg-black/50"
            aria-label={t('nav.closeMenu')}
            onClick={() => setMobileMenuOpen(false)}
          />
          <aside className="relative h-full w-72 max-w-[85vw] bg-surface shadow-2xl">
            {sidebar}
          </aside>
        </div>
      )}

      <div className="md:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border bg-background/90 px-4 backdrop-blur-md sm:px-6 lg:px-8">
          <button
            type="button"
            className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-border md:hidden"
            aria-label={mobileMenuOpen ? t('nav.closeMenu') : t('nav.menu')}
            aria-expanded={mobileMenuOpen}
            onClick={() => setMobileMenuOpen(true)}
          >
            ☰
          </button>
          <form onSubmit={handleQuickSearch} role="search" className="relative min-w-0 w-full max-w-xl">
            <label htmlFor="quick-search" className="sr-only">{t('shell.quickSearch')}</label>
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true">⌕</span>
            <input
              id="quick-search"
              type="search"
              value={quickSearch}
              onChange={event => setQuickSearch(event.target.value)}
              placeholder={t('shell.quickSearchPlaceholder')}
              className="input h-10 pl-10 pr-16 text-sm"
            />
            <kbd aria-hidden="true" className="pointer-events-none absolute right-3 top-1/2 hidden -translate-y-1/2 rounded border border-border px-1.5 py-0.5 text-[10px] text-muted sm:block">
              Enter
            </kbd>
          </form>

          <div className="ml-auto flex shrink-0 items-center gap-2 sm:gap-3">
            <LanguageSelect />
            <ThemeToggle />
            <div className="relative">
              <button
                type="button"
                onClick={() => setProfileMenuOpen(open => !open)}
                className="flex h-10 items-center gap-2 rounded-xl border border-border px-2 transition-colors hover:bg-surface sm:px-3"
                aria-expanded={profileMenuOpen}
                aria-label={t('shell.profileMenu')}
              >
                <span className="grid h-7 w-7 place-items-center rounded-full bg-accent/15 text-xs font-bold text-accent">
                  {user?.name?.slice(0, 1).toUpperCase() ?? 'U'}
                </span>
                <span className="hidden max-w-32 truncate text-sm font-medium sm:block">
                  {user?.name ?? t('shell.myProfile')}
                </span>
                <span className="hidden text-xs text-muted sm:block" aria-hidden="true">⌄</span>
              </button>
              {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-52 rounded-xl border border-border bg-surface p-2 shadow-xl">
                  {isAuthenticated ? (
                    <>
                      <Link to="/profile" className="block rounded-lg px-3 py-2 text-sm hover:bg-background">{t('shell.myProfile')}</Link>
                      <button
                        type="button"
                        onClick={handleLogout}
                        className="block w-full rounded-lg px-3 py-2 text-left text-sm text-danger hover:bg-background"
                      >
                        {t('shell.logout')}
                      </button>
                    </>
                  ) : (
                    <>
                      <Link to="/login" className="block rounded-lg px-3 py-2 text-sm hover:bg-background">{t('shell.login')}</Link>
                      <Link to="/register" className="block rounded-lg px-3 py-2 text-sm hover:bg-background">{t('shell.register')}</Link>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="app-content min-h-[calc(100vh-4rem)] pb-24 md:pb-8">
          {children}
        </main>
      </div>

      <nav aria-label={t('nav.mobile')} className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-5 border-t border-border bg-surface/95 px-1 pb-[env(safe-area-inset-bottom)] pt-2 backdrop-blur-md md:hidden">
        {navigationItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex min-w-0 flex-col items-center gap-0.5 px-1 py-1 text-[10px] leading-tight ${
                isActive ? 'font-semibold text-accent' : 'text-muted'
              }`
            }
          >
            <span className="text-xl leading-none" aria-hidden="true">{item.icon}</span>
            <span className="max-w-full truncate">{t(item.shortLabel ?? item.label)}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
