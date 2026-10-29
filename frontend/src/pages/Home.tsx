import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { dealsService } from '../services'
import ProductCard from '../components/ProductCard'
import type { OfferWithDeal } from '../types'

export default function Home() {
  const [deals, setDeals] = useState<OfferWithDeal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dealsService
      .getDeals({ limit: 6 })
      .then(r => setDeals(r.data))
      .catch(() => setDeals([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <main className="max-w-7xl mx-auto px-4 py-10">
      {/* Hero */}
      <section className="text-center mb-16">
        <div className="inline-flex items-center gap-2 bg-accent/10 text-accent text-xs font-medium px-3 py-1 rounded-full mb-4">
          <span>✦</span> Powered by AI
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight">
          As melhores ofertas de<br />
          <span className="text-accent">tecnologia</span>, em um lugar.
        </h1>
        <p className="text-muted text-lg mb-8 max-w-xl mx-auto">
          Pesquise em linguagem natural, monitore preços e receba alertas quando o produto cair de preço.
        </p>
        <div className="flex items-center justify-center gap-3 flex-wrap">
          <Link to="/ai-search" className="btn-primary text-base px-6 py-3">
            ✦ Busca com IA
          </Link>
          <Link to="/search" className="btn-secondary text-base px-6 py-3">
            Busca avançada
          </Link>
        </div>
      </section>

      {/* Top Deals */}
      <section>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-semibold text-white">🔥 Melhores ofertas agora</h2>
          <Link to="/deals" className="text-sm text-accent hover:underline">Ver todas →</Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="card h-48 animate-pulse bg-border" />
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-muted">Nenhuma oferta disponível no momento.</p>
            <p className="text-sm text-muted mt-1">
              Use a{' '}
              <Link to="/search" className="text-accent hover:underline">busca ao vivo</Link>
              {' '}para descobrir produtos do Mercado Livre.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {deals.map(offer => (
              <ProductCard key={offer.id} offer={offer} />
            ))}
          </div>
        )}
      </section>

      {/* Features */}
      <section className="grid sm:grid-cols-3 gap-6 mt-16">
        {[
          { icon: '🔍', title: 'Busca Inteligente', desc: 'Descreva o produto em português e a IA extrai os filtros certos.' },
          { icon: '📈', title: 'Histórico de Preços', desc: 'Veja se o preço atual é realmente bom comparado ao histórico.' },
          { icon: '🔔', title: 'Alertas de Preço', desc: 'Defina seu preço alvo e seja notificado quando atingido.' },
        ].map(f => (
          <div key={f.title} className="card flex flex-col gap-2">
            <span className="text-2xl">{f.icon}</span>
            <h3 className="text-white font-semibold">{f.title}</h3>
            <p className="text-muted text-sm">{f.desc}</p>
          </div>
        ))}
      </section>
    </main>
  )
}
