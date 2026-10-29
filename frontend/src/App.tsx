import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import Navbar from './components/Navbar'

import Home from './pages/Home'
import Search from './pages/Search'
import AISearch from './pages/AISearch'
import Deals from './pages/Deals'
import Favorites from './pages/Favorites'
import Alerts from './pages/Alerts'
import Login from './pages/Login'
import Register from './pages/Register'
import Admin from './pages/Admin'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <div className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<Search />} />
              <Route path="/ai-search" element={<AISearch />} />
              <Route path="/deals" element={<Deals />} />
              <Route path="/favorites" element={<Favorites />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="*" element={
                <main className="max-w-xl mx-auto px-4 py-20 text-center">
                  <h1 className="text-4xl font-bold text-white mb-2">404</h1>
                  <p className="text-muted">Página não encontrada.</p>
                </main>
              } />
            </Routes>
          </div>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}
