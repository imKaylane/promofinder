import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

export type Language = 'pt' | 'en' | 'es'
type Message = readonly [portuguese: string, english: string, spanish: string]

const messages = {
  'app.title': ['promoFinder — Ofertas de PC e periféricos', 'promoFinder — PC and peripheral deals', 'promoFinder — Ofertas de PC y periféricos'],
  'nav.home': ['Início', 'Home', 'Inicio'],
  'nav.search': ['Buscar produtos', 'Search products', 'Buscar productos'],
  'nav.searchShort': ['Buscar', 'Search', 'Buscar'],
  'nav.alerts': ['Alertas de preço', 'Price alerts', 'Alertas de precio'],
  'nav.alertsShort': ['Alertas', 'Alerts', 'Alertas'],
  'nav.favorites': ['Favoritos', 'Favorites', 'Favoritos'],
  'nav.profile': ['Perfil e configurações', 'Profile and settings', 'Perfil y ajustes'],
  'nav.profileShort': ['Perfil', 'Profile', 'Perfil'],
  'nav.deals': ['Ofertas', 'Deals', 'Ofertas'],
  'nav.aiSearch': ['Busca com IA', 'AI search', 'Búsqueda con IA'],
  'nav.admin': ['Administração', 'Administration', 'Administración'],
  'nav.menu': ['Menu', 'Menu', 'Menú'],
  'nav.closeMenu': ['Fechar menu', 'Close menu', 'Cerrar menú'],
  'nav.discover': ['Descobrir', 'Discover', 'Descubrir'],
  'nav.primary': ['Navegação principal', 'Main navigation', 'Navegación principal'],
  'nav.mobile': ['Navegação mobile', 'Mobile navigation', 'Navegación móvil'],
  'shell.footerTitle': ['Encontre o melhor preço', 'Find the best price', 'Encuentra el mejor precio'],
  'shell.footerText': ['Acompanhe ofertas e economize.', 'Track deals and save.', 'Sigue ofertas y ahorra.'],
  'shell.quickSearch': ['Busca rápida', 'Quick search', 'Búsqueda rápida'],
  'shell.quickSearchPlaceholder': ['Buscar produtos e ofertas...', 'Search products and deals...', 'Buscar productos y ofertas...'],
  'shell.themeToLight': ['Ativar tema claro', 'Switch to light theme', 'Activar tema claro'],
  'shell.themeToDark': ['Ativar tema escuro', 'Switch to dark theme', 'Activar tema oscuro'],
  'shell.profileMenu': ['Menu do perfil', 'Profile menu', 'Menú de perfil'],
  'shell.myProfile': ['Meu perfil', 'My profile', 'Mi perfil'],
  'shell.logout': ['Sair da conta', 'Sign out', 'Cerrar sesión'],
  'shell.login': ['Entrar', 'Sign in', 'Iniciar sesión'],
  'shell.register': ['Criar conta', 'Create account', 'Crear cuenta'],
  'preferences.language': ['Idioma', 'Language', 'Idioma'],
  'preferences.portuguese': ['Português', 'Português', 'Portugués'],
  'preferences.english': ['English', 'English', 'English'],
  'preferences.spanish': ['Español', 'Español', 'Español'],
  'error.notFoundTitle': ['Página não encontrada', 'Page not found', 'Página no encontrada'],
  'home.featuredSection': ['Destaques promocionais', 'Featured deals', 'Ofertas destacadas'],
  'home.featuredLabel': ['DESTAQUE PROMOFINDER', 'PROMOFINDER FEATURE', 'DESTACADO PROMOFINDER'],
  'home.featuredFallback': ['Oferta selecionada para você', 'A deal picked for you', 'Una oferta seleccionada para ti'],
  'home.headline': ['Oportunidades para comprar melhor.', 'Better ways to shop.', 'Oportunidades para comprar mejor.'],
  'home.buy': ['Aproveitar oferta', 'Get this deal', 'Aprovechar oferta'],
  'home.explore': ['Explorar ofertas', 'Explore deals', 'Explorar ofertas'],
  'home.updatedRegularly': ['Ofertas atualizadas em ciclos ao longo do dia.', 'Deals refresh in cycles throughout the day.', 'Las ofertas se actualizan en ciclos a lo largo del día.'],
  'home.previous': ['Destaque anterior', 'Previous highlight', 'Oferta destacada anterior'],
  'home.next': ['Próximo destaque', 'Next highlight', 'Siguiente oferta destacada'],
  'home.featuredPosition': ['Destaque {current} de {total}', 'Highlight {current} of {total}', 'Oferta {current} de {total}'],
  'home.showHighlight': ['Ver destaque {number}', 'View highlight {number}', 'Ver oferta {number}'],
  'home.defaultHeadline': ['Boas ofertas, sem perder tempo.', 'Great deals, without the hassle.', 'Buenas ofertas, sin perder tiempo.'],
  'home.defaultDescription': ['Explore produtos e acompanhe os preços para encontrar a hora certa de comprar.', 'Explore products and track prices to find the right time to buy.', 'Explora productos y sigue sus precios para encontrar el mejor momento para comprar.'],
  'home.searchProducts': ['Buscar produtos', 'Search products', 'Buscar productos'],
  'home.find': ['Encontre o que procura', 'Find what you need', 'Encuentra lo que buscas'],
  'home.exploreCategories': ['Explore categorias', 'Browse categories', 'Explorar categorías'],
  'home.categoryPC': ['Peças de PC', 'PC components', 'Componentes de PC'],
  'home.categoryPeripherals': ['Periféricos', 'Peripherals', 'Periféricos'],
  'home.selectedForYou': ['Selecionadas para você', 'Picked for you', 'Seleccionadas para ti'],
  'home.featuredDeals': ['Ofertas em destaque', 'Featured deals', 'Ofertas destacadas'],
  'home.viewAll': ['Ver todas', 'View all', 'Ver todas'],
  'home.favoriteError': ['Não foi possível carregar o estado dos seus favoritos.', 'Could not load your favorites.', 'No se pudieron cargar tus favoritos.'],
  'home.favoriteWarning': ['O botão de favorito pode não refletir itens salvos anteriormente.', 'Favorite buttons may not reflect previously saved items.', 'Los botones de favoritos podrían no reflejar elementos guardados anteriormente.'],
  'home.tryAgain': ['Tentar novamente', 'Try again', 'Intentar de nuevo'],
  'home.emptyTitle': ['Ainda não há ofertas para mostrar.', 'No deals to show yet.', 'Todavía no hay ofertas para mostrar.'],
  'home.emptyText': ['Faça uma busca para encontrar produtos disponíveis.', 'Search to find available products.', 'Busca productos disponibles.'],
  'home.error': ['Não foi possível carregar as ofertas. Confira sua conexão e tente novamente.', 'Could not load deals. Check your connection and try again.', 'No se pudieron cargar las ofertas. Comprueba tu conexión e inténtalo de nuevo.'],
  'search.title': ['Busca de produtos', 'Product search', 'Búsqueda de productos'],
  'search.example': ['Ex.: RTX 4060, Ryzen 7, monitor 144 Hz...', 'E.g. RTX 4060, Ryzen 7, 144 Hz monitor...', 'Ej.: RTX 4060, Ryzen 7, monitor 144 Hz...'],
  'search.submit': ['Buscar', 'Search', 'Buscar'],
  'search.loading': ['Buscando…', 'Searching…', 'Buscando…'],
  'search.explore': ['Explorar:', 'Explore:', 'Explorar:'],
  'search.categoryPC': ['Peças de PC', 'PC components', 'Componentes de PC'],
  'search.categoryPeripherals': ['Periféricos', 'Peripherals', 'Periféricos'],
  'search.minPrice': ['Preço mínimo (R$)', 'Minimum price (R$)', 'Precio mínimo (R$)'],
  'search.maxPrice': ['Preço máximo (R$)', 'Maximum price (R$)', 'Precio máximo (R$)'],
  'search.condition': ['Condição', 'Condition', 'Condición'],
  'search.allConditions': ['Todas', 'Any', 'Todas'],
  'search.new': ['Novo', 'New', 'Nuevo'],
  'search.used': ['Usado', 'Used', 'Usado'],
  'search.sort': ['Ordenar por', 'Sort by', 'Ordenar por'],
  'search.relevance': ['Relevância', 'Relevance', 'Relevancia'],
  'search.lowestPrice': ['Menor preço', 'Lowest price', 'Menor precio'],
  'search.highestPrice': ['Maior preço', 'Highest price', 'Mayor precio'],
  'search.oneResult': ['1 resultado para "{query}"', '1 result for "{query}"', '1 resultado para "{query}"'],
  'search.results': ['{count} resultados para "{query}"', '{count} results for "{query}"', '{count} resultados para "{query}"'],
  'search.loadMore': ['Carregar mais ofertas', 'Load more deals', 'Cargar más ofertas'],
  'search.none': ['Nenhum resultado encontrado.', 'No results found.', 'No se encontraron resultados.'],
  'search.tryAgain': ['Tente outros termos ou ajuste os filtros.', 'Try different terms or adjust the filters.', 'Prueba otros términos o ajusta los filtros.'],
  'search.error': ['Erro ao buscar produtos. Verifique sua conexão e tente novamente.', 'Search failed. Check your connection and try again.', 'La búsqueda falló. Comprueba tu conexión e inténtalo de nuevo.'],
  'ai.title': ['Busca com Inteligência Artificial', 'AI-powered search', 'Búsqueda con inteligencia artificial'],
  'ai.shortTitle': ['Busca com IA', 'AI search', 'Búsqueda con IA'],
  'ai.loginRequired': ['Faça login para usar a busca inteligente com inteligência artificial.', 'Sign in to use AI-powered search.', 'Inicia sesión para usar la búsqueda inteligente con IA.'],
  'ai.description': ['Descreva o que você procura em linguagem natural. A IA extrai os filtros e busca no Mercado Livre.', 'Describe what you need in natural language. AI extracts filters and searches Mercado Livre.', 'Describe lo que buscas con lenguaje natural. La IA extrae los filtros y busca en Mercado Livre.'],
  'ai.example': ['Ex.: Processador Ryzen 7 até R$ 1.500, placa de vídeo em conta…', 'E.g. Ryzen 7 processor under R$1,500, affordable graphics card…', 'Ej.: Procesador Ryzen 7 hasta R$1.500, tarjeta gráfica económica…'],
  'ai.example1': ['Processador Ryzen 7 até R$ 1.500', 'Ryzen 7 processor under R$1,500', 'Procesador Ryzen 7 hasta R$1.500'],
  'ai.example2': ['Placa de vídeo com bom custo-benefício', 'Good-value graphics card', 'Tarjeta gráfica con buena relación calidad-precio'],
  'ai.example3': ['Notebook gamer até R$ 4.000', 'Gaming laptop under R$4,000', 'Portátil gaming hasta R$4.000'],
  'ai.example4': ['SSD NVMe 1TB', '1TB NVMe SSD', 'SSD NVMe de 1 TB'],
  'ai.interpreted': ['Consulta interpretada pela IA', 'Query interpreted by AI', 'Consulta interpretada por la IA'],
  'ai.notConfigured': ['⚠ IA não configurada — filtros extraídos por regras locais.', '⚠ AI is not configured — filters were extracted locally.', '⚠ IA no configurada: filtros extraídos localmente.'],
  'ai.summary': ['Análise da IA', 'AI analysis', 'Análisis de IA'],
  'ai.productsFound': ['{count} produto(s) encontrado(s)', '{count} product(s) found', '{count} producto(s) encontrado(s)'],
  'ai.none': ['Nenhum produto encontrado. Tente reformular a busca.', 'No products found. Try changing your search.', 'No se encontraron productos. Prueba otra búsqueda.'],
  'ai.error': ['Erro ao processar busca. Tente novamente.', 'Search failed. Please try again.', 'Error al procesar la búsqueda. Inténtalo de nuevo.'],
  'deals.title': ['Ofertas em destaque', 'Featured deals', 'Ofertas destacadas'],
  'deals.description': ['Ofertas de peças de PC e periféricos.', 'Deals on PC parts and peripherals.', 'Ofertas de componentes de PC y periféricos.'],
  'deals.categoryTitle': ['{category} em promoção', 'Deals on {category}', 'Ofertas de {category}'],
  'deals.categoryDescription': ['Ofertas filtradas desta categoria.', 'Deals filtered to this category.', 'Ofertas filtradas de esta categoría.'],
  'deals.items': ['{count} itens', '{count} items', '{count} artículos'],
  'deals.none': ['Nenhuma oferta disponível ainda.', 'No deals available yet.', 'Todavía no hay ofertas disponibles.'],
  'deals.noneText': ['Faça uma busca ao vivo para encontrar produtos disponíveis.', 'Run a live search to find available products.', 'Haz una búsqueda en vivo para encontrar productos disponibles.'],
  'deals.categoryNone': ['Nenhuma oferta de {category} encontrada.', 'No {category} deals found.', 'No se encontraron ofertas de {category}.'],
  'deals.categoryNoneText': ['As ofertas aparecem aqui quando houver produtos desta categoria.', 'Deals will appear here when products in this category are available.', 'Las ofertas aparecerán aquí cuando haya productos de esta categoría.'],
  'deals.error': ['Não foi possível carregar as ofertas. Verifique sua conexão e tente novamente.', 'Could not load deals. Check your connection and try again.', 'No se pudieron cargar las ofertas. Comprueba tu conexión e inténtalo de nuevo.'],
  'favorites.title': ['Meus favoritos', 'My favorites', 'Mis favoritos'],
  'favorites.loginRequired': ['Faça login para gerenciar seus favoritos.', 'Sign in to manage your favorites.', 'Inicia sesión para gestionar tus favoritos.'],
  'favorites.none': ['Você ainda não tem favoritos.', 'You have no favorites yet.', 'Todavía no tienes favoritos.'],
  'favorites.search': ['Buscar produtos →', 'Search products →', 'Buscar productos →'],
  'favorites.added': ['Adicionado em {date}', 'Added on {date}', 'Añadido el {date}'],
  'favorites.remove': ['Remover', 'Remove', 'Eliminar'],
  'alerts.title': ['Alertas de preço', 'Price alerts', 'Alertas de precio'],
  'alerts.loginRequired': ['Faça login para gerenciar seus alertas.', 'Sign in to manage your alerts.', 'Inicia sesión para gestionar tus alertas.'],
  'alerts.new': ['Novo alerta', 'New alert', 'Nueva alerta'],
  'alerts.productId': ['ID do produto (UUID do banco)', 'Product ID (database UUID)', 'ID del producto (UUID de la base de datos)'],
  'alerts.targetPrice': ['Preço alvo (R$)', 'Target price (R$)', 'Precio objetivo (R$)'],
  'alerts.create': ['Criar alerta', 'Create alert', 'Crear alerta'],
  'alerts.error': ['Erro ao criar alerta. Verifique o ID do produto.', 'Could not create alert. Check the product ID.', 'No se pudo crear la alerta. Comprueba el ID del producto.'],
  'alerts.none': ['Você não tem alertas ativos.', 'You have no active alerts.', 'No tienes alertas activos.'],
  'alerts.product': ['Produto:', 'Product:', 'Producto:'],
  'alerts.activeCreated': ['Ativo — criado em {date}', 'Active — created on {date}', 'Activo — creado el {date}'],
  'alerts.triggered': ['✅ Alerta disparado', '✅ Alert triggered', '✅ Alerta activada'],
  'alerts.delete': ['Excluir', 'Delete', 'Eliminar'],
  'login.title': ['Entrar', 'Sign in', 'Iniciar sesión'],
  'login.subtitle': ['Acesse sua conta promoFinder', 'Access your promoFinder account', 'Accede a tu cuenta de promoFinder'],
  'login.email': ['E-mail', 'Email', 'Correo electrónico'],
  'login.password': ['Senha', 'Password', 'Contraseña'],
  'login.emailPlaceholder': ['seu@email.com', 'you@email.com', 'tu@email.com'],
  'login.error': ['E-mail ou senha incorretos.', 'Incorrect email or password.', 'Correo o contraseña incorrectos.'],
  'login.loading': ['Entrando…', 'Signing in…', 'Iniciando sesión…'],
  'login.noAccount': ['Não tem conta?', 'Don’t have an account?', '¿No tienes cuenta?'],
  'register.title': ['Criar conta', 'Create account', 'Crear cuenta'],
  'register.subtitle': ['Comece a monitorar ofertas gratuitamente', 'Start tracking deals for free', 'Empieza a seguir ofertas gratis'],
  'register.name': ['Nome', 'Name', 'Nombre'],
  'register.namePlaceholder': ['Seu nome', 'Your name', 'Tu nombre'],
  'register.passwordHint': ['8 a 72 caracteres', '8 to 72 characters', 'De 8 a 72 caracteres'],
  'register.passwordShort': ['A senha deve ter pelo menos 8 caracteres.', 'Password must be at least 8 characters.', 'La contraseña debe tener al menos 8 caracteres.'],
  'register.emailExists': ['Este e-mail já está cadastrado. Tente entrar ou use outro e-mail.', 'This email is already registered. Sign in or use another email.', 'Este correo ya está registrado. Inicia sesión o usa otro correo.'],
  'register.emailInvalid': ['Informe um endereço de e-mail válido.', 'Enter a valid email address.', 'Introduce un correo electrónico válido.'],
  'register.nameShort': ['O nome deve ter pelo menos 2 caracteres.', 'Name must be at least 2 characters.', 'El nombre debe tener al menos 2 caracteres.'],
  'register.passwordLength': ['A senha deve ter de 8 a 72 bytes.', 'Password must be 8 to 72 bytes long.', 'La contraseña debe tener entre 8 y 72 bytes.'],
  'register.invalidForm': ['Confira os dados do formulário e tente novamente.', 'Check the form details and try again.', 'Revisa los datos del formulario e inténtalo de nuevo.'],
  'register.error': ['Não foi possível criar a conta. Tente novamente.', 'Could not create the account. Please try again.', 'No se pudo crear la cuenta. Inténtalo de nuevo.'],
  'register.loading': ['Criando conta…', 'Creating account…', 'Creando cuenta…'],
  'register.haveAccount': ['Já tem conta?', 'Already have an account?', '¿Ya tienes una cuenta?'],
  'profile.title': ['Perfil e configurações', 'Profile and settings', 'Perfil y ajustes'],
  'profile.loginRequired': ['Entre na sua conta para ver os dados do perfil.', 'Sign in to view your profile.', 'Inicia sesión para ver tu perfil.'],
  'profile.account': ['Sua conta', 'Your account', 'Tu cuenta'],
  'profile.accountLabel': ['Conta', 'Account', 'Cuenta'],
  'profile.description': ['Gerencie seus dados e preferências do promoFinder.', 'Manage your promoFinder details and preferences.', 'Gestiona tus datos y preferencias de promoFinder.'],
  'profile.info': ['Informações do perfil', 'Profile information', 'Información del perfil'],
  'profile.accountType': ['Tipo de conta', 'Account type', 'Tipo de cuenta'],
  'profile.admin': ['Administrador', 'Administrator', 'Administrador'],
  'profile.user': ['Usuário', 'User', 'Usuario'],
  'profile.active': ['Ativa', 'Active', 'Activa'],
  'profile.inactive': ['Inativa', 'Inactive', 'Inactiva'],
  'profile.meli': ['Mercado Livre', 'Mercado Livre', 'Mercado Livre'],
  'profile.meliConnected': ['Sua conta do Mercado Livre está conectada para as buscas.', 'Your Mercado Livre account is connected for searches.', 'Tu cuenta de Mercado Livre está conectada para las búsquedas.'],
  'profile.meliNotConnected': ['Conecte uma conta autorizada para permitir o acesso da aplicação à API.', 'Connect an authorized account to allow the app to access the API.', 'Conecta una cuenta autorizada para permitir que la aplicación acceda a la API.'],
  'profile.connectAgain': ['Conectar outra vez', 'Reconnect', 'Conectar de nuevo'],
  'profile.connectMeli': ['Conectar Mercado Livre', 'Connect Mercado Livre', 'Conectar Mercado Livre'],
  'profile.preferences': ['Preferências', 'Preferences', 'Preferencias'],
  'profile.themeDescription': ['Escolha o tema e o idioma nos controles do cabeçalho. As preferências ficam salvas neste dispositivo.', 'Choose the theme and language from the header controls. Your preferences are saved on this device.', 'Elige el tema y el idioma en los controles del encabezado. Las preferencias se guardan en este dispositivo.'],
  'admin.title': ['Painel Admin', 'Admin dashboard', 'Panel de administración'],
  'admin.users': ['Usuários', 'Users', 'Usuarios'],
  'admin.products': ['Produtos', 'Products', 'Productos'],
  'admin.alerts': ['Alertas', 'Alerts', 'Alertas'],
  'admin.name': ['Nome', 'Name', 'Nombre'],
  'admin.email': ['E-mail', 'Email', 'Correo electrónico'],
  'admin.role': ['Papel', 'Role', 'Rol'],
  'admin.joined': ['Cadastro', 'Joined', 'Registro'],
  'admin.status': ['Status', 'Status', 'Estado'],
  'admin.active': ['Ativo', 'Active', 'Activo'],
  'admin.inactive': ['Inativo', 'Inactive', 'Inactivo'],
  'admin.deactivate': ['Desativar', 'Deactivate', 'Desactivar'],
  'admin.activate': ['Ativar', 'Activate', 'Activar'],
  'meli.title': ['Conexão com Mercado Livre', 'Mercado Livre connection', 'Conexión con Mercado Livre'],
  'meli.connecting': ['Conectando sua conta do Mercado Livre...', 'Connecting your Mercado Livre account...', 'Conectando tu cuenta de Mercado Livre...'],
  'meli.authorizationError': ['A autorização no Mercado Livre não foi concluída.', 'Mercado Livre authorization was not completed.', 'No se completó la autorización en Mercado Livre.'],
  'meli.incomplete': ['O retorno do Mercado Livre está incompleto. Tente conectar novamente.', 'The Mercado Livre response is incomplete. Please reconnect.', 'La respuesta de Mercado Livre está incompleta. Intenta conectar de nuevo.'],
  'meli.connected': ['Conta do Mercado Livre conectada com sucesso.', 'Mercado Livre account connected successfully.', 'Cuenta de Mercado Livre conectada correctamente.'],
  'meli.failed': ['Não foi possível concluir a conexão. Verifique a configuração e tente novamente.', 'Could not complete the connection. Check the configuration and try again.', 'No se pudo completar la conexión. Comprueba la configuración e inténtalo de nuevo.'],
  'meli.backProfile': ['Voltar ao perfil', 'Back to profile', 'Volver al perfil'],
  'product.new': ['Novo', 'New', 'Nuevo'],
  'product.used': ['Usado', 'Used', 'Usado'],
  'product.viewOffer': ['Ver oferta', 'View deal', 'Ver oferta'],
  'product.favoriteAdd': ['Adicionar aos favoritos', 'Add to favorites', 'Añadir a favoritos'],
  'product.favoriteRemove': ['Remover dos favoritos', 'Remove from favorites', 'Quitar de favoritos'],
  'product.favoriteError': ['Não foi possível atualizar o favorito.', 'Could not update favorite.', 'No se pudo actualizar el favorito.'],
  'product.freeShipping': ['Frete grátis', 'Free shipping', 'Envío gratis'],
  'deal.lowestHistory': ['🔥 Menor preço histórico', '🔥 Lowest recorded price', '🔥 Precio mínimo histórico'],
  'deal.priceDrop': ['📉 Queda detectada', '📉 Price drop detected', '📉 Bajada detectada'],
  'deal.potential': ['⚡ Promoção potencial', '⚡ Potential deal', '⚡ Oferta potencial'],
  'deal.regular': ['Preço normal', 'Regular price', 'Precio habitual'],
  'deal.insufficientHistory': ['Histórico insuficiente', 'Not enough price history', 'Historial insuficiente'],
  'deal.outdated': ['Dados desatualizados', 'Outdated data', 'Datos desactualizados'],
} as const satisfies Record<string, Message>

export type TranslationKey = keyof typeof messages

const languageIndex: Record<Language, 0 | 1 | 2> = { pt: 0, en: 1, es: 2 }
const locale: Record<Language, string> = { pt: 'pt-BR', en: 'en-US', es: 'es-ES' }

function isLanguage(value: string | null): value is Language {
  return value === 'pt' || value === 'en' || value === 'es'
}

interface LanguageContextValue {
  language: Language
  setLanguage: (language: Language) => void
  locale: string
  t: (key: TranslationKey, values?: Record<string, string | number>) => string
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    const saved = window.localStorage.getItem('language')
    return isLanguage(saved) ? saved : 'pt'
  })

  const t = useCallback((key: TranslationKey, values: Record<string, string | number> = {}) => {
    let text: string = messages[key][languageIndex[language]]
    for (const [name, value] of Object.entries(values)) {
      text = text.split(`{${name}}`).join(String(value))
    }
    return text
  }, [language])

  useEffect(() => {
    document.documentElement.lang = locale[language]
    document.title = t('app.title')
    window.localStorage.setItem('language', language)
  }, [language])

  const value = useMemo(
    () => ({ language, setLanguage, locale: locale[language], t }),
    [language, t],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) throw new Error('useLanguage must be used within LanguageProvider')
  return context
}
