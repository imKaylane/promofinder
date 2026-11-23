import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import AppShell from './components/AppShell'
import { LanguageProvider, useLanguage } from './i18n'
import { ThemeProvider } from './theme'

import Home from './pages/Home'
import Search from './pages/Search'
import AISearch from './pages/AISearch'
import Deals from './pages/Deals'
import CategoryDeals from './pages/CategoryDeals'
import Favorites from './pages/Favorites'
import Alerts from './pages/Alerts'
import Login from './pages/Login'
import Register from './pages/Register'
import Admin from './pages/Admin'
import Profile from './pages/Profile'
import MercadoLivreCallback from './pages/MercadoLivreCallback'

function RoutedApp() {
  const { t } = useLanguage()

  return (
    <Routes>
      <Route path="/login" element={<div className="app-content min-h-screen"><Login /></div>} />
      <Route path="/register" element={<div className="app-content min-h-screen"><Register /></div>} />
      <Route path="/auth/mercadolivre/callback" element={<MercadoLivreCallback />} />
      <Route path="*" element={
        <AppShell>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Search />} />
            <Route path="/ai-search" element={<AISearch />} />
            <Route path="/deals" element={<Deals />} />
            <Route path="/categories/:slug" element={<CategoryDeals />} />
            <Route path="/favorites" element={<Favorites />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={
              <main className="mx-auto max-w-xl px-4 py-20 text-center">
                <h1 className="mb-2 text-4xl font-bold">404</h1>
                <p className="text-muted">{t('error.notFoundTitle')}</p>
              </main>
            } />
          </Routes>
        </AppShell>
      } />
    </Routes>
  )
}

export default function App() {
  return (
    <LanguageProvider>
      <ThemeProvider>
        <BrowserRouter>
          <AuthProvider>
            <RoutedApp />
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </LanguageProvider>
  )
}
