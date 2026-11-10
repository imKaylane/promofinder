// =========================================================
// GestãoPro — Layout Shell (Sidebar, Header, Hamburger)
// EX1: navegação compartilhada, hamburger menu
// =========================================================

const Layout = (() => {
  function init() {
    _buildShell();
    _setupHamburger();
    _markActive();
  }

  function _buildShell() {
    const shellEl = document.getElementById('app-shell');
    if (!shellEl) return;

    const page = shellEl.getAttribute('data-page') || '';
    const title = shellEl.getAttribute('data-title') || 'GestãoPro';
    const userStr = sessionStorage.getItem('gestaopro_user');
    const user = userStr ? JSON.parse(userStr) : null;
    const initials = user ? user.name.charAt(0).toUpperCase() : 'U';

    const navLinks = [
      { href: '../pages/dashboard.html', icon: '📊', key: 'nav.dashboard', id: 'dashboard' },
      { href: '../pages/clientes.html',  icon: '👥', key: 'nav.customers',  id: 'clientes' },
      { href: '../pages/fornecedores.html', icon: '🏭', key: 'nav.suppliers', id: 'fornecedores' },
      { href: '../pages/produtos.html',  icon: '📦', key: 'nav.products',   id: 'produtos' },
      { href: '../pages/vendas.html',    icon: '🛒', key: 'nav.sales',      id: 'vendas' },
      { href: '../pages/pedidos.html',   icon: '📋', key: 'nav.orders',     id: 'pedidos' },
      { href: '../pages/estoque.html',   icon: '🏪', key: 'nav.stock',      id: 'estoque' },
      { href: '../pages/financeiro.html',icon: '💰', key: 'nav.financial',  id: 'financeiro' },
      { href: '../pages/calculadora.html',icon: '🧮',key: 'nav.calculator', id: 'calculadora' },
      { href: '../pages/usuarios.html',  icon: '⚙️', key: 'nav.users',      id: 'usuarios', adminOnly: true },
      { href: '../pages/auditoria.html', icon: '🔍', key: 'nav.audit',      id: 'auditoria', adminOnly: true },
    ];

    const mainLinks = navLinks.filter(l => !l.adminOnly);
    const adminLinks = navLinks.filter(l => l.adminOnly);
    const isAdmin = user && user.role === 'admin';

    shellEl.innerHTML = `
      <div class="sidebar-overlay" id="sidebar-overlay"></div>
      <aside class="sidebar" id="sidebar" role="navigation" aria-label="Menu principal">
        <a href="../pages/dashboard.html" class="sidebar-logo">
          <div class="sidebar-logo-icon">G</div>
          <div>
            <div class="sidebar-logo-text">GestãoPro</div>
            <div class="sidebar-logo-sub">ERP</div>
          </div>
        </a>
        <nav class="sidebar-nav">
          <div class="sidebar-section-title" data-i18n="nav.section_main"></div>
          ${mainLinks.map(l => `
            <a href="${l.href}" class="sidebar-link" data-nav="${l.id}">
              <span class="sidebar-link-icon">${l.icon}</span>
              <span class="sidebar-link-label" data-i18n="${l.key}"></span>
            </a>
          `).join('')}
          ${isAdmin ? `
            <div class="sidebar-section-title" data-i18n="nav.section_admin"></div>
            ${adminLinks.map(l => `
              <a href="${l.href}" class="sidebar-link" data-nav="${l.id}">
                <span class="sidebar-link-icon">${l.icon}</span>
                <span class="sidebar-link-label" data-i18n="${l.key}"></span>
              </a>
            `).join('')}
          ` : ''}
        </nav>
      </aside>

      <header class="header" role="banner">
        <div class="header-left">
          <button class="hamburger" id="hamburger-btn" aria-label="Abrir menu" aria-expanded="false">
            <span></span><span></span><span></span>
          </button>
          <div>
            <div class="header-title" id="header-title">${title}</div>
          </div>
        </div>
        <div class="header-right">
          <button class="lang-selector" id="lang-toggle" aria-label="Trocar idioma"></button>
          <div class="header-user">
            <div class="header-avatar">${initials}</div>
            <span id="header-username">${user ? user.name : ''}</span>
          </div>
          <button class="btn btn-secondary btn-sm" id="btn-logout" data-i18n="auth.logout"></button>
        </div>
      </header>

      <main class="main" id="main-content" role="main">
        <!-- conteúdo da página inserido aqui -->
      </main>
    `;

    // Wire lang toggle
    document.getElementById('lang-toggle')?.addEventListener('click', () => I18N.toggle());

    // Wire logout
    document.getElementById('btn-logout')?.addEventListener('click', () => Auth.logout());

    // Wire overlay
    document.getElementById('sidebar-overlay')?.addEventListener('click', _closeSidebar);
  }

  function _setupHamburger() {
    const btn = document.getElementById('hamburger-btn');
    if (!btn) return;
    btn.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      const overlay = document.getElementById('sidebar-overlay');
      const open = sidebar.classList.toggle('open');
      overlay.classList.toggle('open', open);
      btn.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open);
    });
  }

  function _closeSidebar() {
    document.getElementById('sidebar')?.classList.remove('open');
    document.getElementById('sidebar-overlay')?.classList.remove('open');
    document.getElementById('hamburger-btn')?.classList.remove('open');
  }

  function _markActive() {
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
      const href = link.getAttribute('href') || '';
      if (path.endsWith(href.replace('../pages/', '').replace('./', ''))) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      }
    });
  }

  function setContent(html) {
    const main = document.getElementById('main-content');
    if (main) main.innerHTML = html;
  }

  return { init, setContent };
})();
