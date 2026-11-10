// =========================================================
// GestãoPro — Layout Shell (EX1)
// Gera HTML5 semântico: <aside><nav>, <header>, <main>, <footer>
// Hamburger com aria-expanded, fecha em link/overlay/Esc
// =========================================================

const Layout = (() => {

  function init() {
    _buildShell();
    _setupHamburger();
    _markActive();
    // Re-apply i18n after building the shell
    if (typeof I18N !== 'undefined') I18N.applyAll();
  }

  function _buildShell() {
    const shellEl = document.getElementById('app-shell');
    if (!shellEl) return;

    const page  = shellEl.getAttribute('data-page') || '';
    const title = shellEl.getAttribute('data-title') || 'GestãoPro';
    const userStr = sessionStorage.getItem('gestaopro_user');
    const user    = userStr ? JSON.parse(userStr) : null;
    const initials = user ? user.name.charAt(0).toUpperCase() : 'U';
    const isAdmin  = user && user.role === 'admin';

    const mainLinks = [
      { href: '/frontend/pages/dashboard.html',   icon: '📊', key: 'nav.dashboard',  id: 'dashboard' },
      { href: '/frontend/pages/clientes.html',    icon: '👥', key: 'nav.customers',  id: 'clientes' },
      { href: '/frontend/pages/fornecedores.html',icon: '🏭', key: 'nav.suppliers',  id: 'fornecedores' },
      { href: '/frontend/pages/produtos.html',    icon: '📦', key: 'nav.products',   id: 'produtos' },
      { href: '/frontend/pages/vendas.html',      icon: '🛒', key: 'nav.sales',      id: 'vendas' },
      { href: '/frontend/pages/pedidos.html',     icon: '📋', key: 'nav.orders',     id: 'pedidos' },
      { href: '/frontend/pages/estoque.html',     icon: '🏪', key: 'nav.stock',      id: 'estoque' },
      { href: '/frontend/pages/financeiro.html',  icon: '💰', key: 'nav.financial',  id: 'financeiro' },
      { href: '/frontend/pages/calculadora.html', icon: '🧮', key: 'nav.calculator', id: 'calculadora' },
    ];
    const adminLinks = [
      { href: '/frontend/pages/usuarios.html',    icon: '⚙️', key: 'nav.users',      id: 'usuarios' },
      { href: '/frontend/pages/auditoria.html',   icon: '🔍', key: 'nav.audit',      id: 'auditoria' },
    ];

    const _navItem = l =>
      `<a href="${l.href}" class="sidebar-link" data-nav="${l.id}" aria-label="${l.id}">
        <span class="sidebar-link-icon" aria-hidden="true">${l.icon}</span>
        <span class="sidebar-link-label" data-i18n="${l.key}"></span>
      </a>`;

    shellEl.innerHTML = `
      <div class="sidebar-overlay" id="sidebar-overlay" role="presentation"></div>

      <aside class="sidebar" id="sidebar">
        <a href="/" class="sidebar-logo" aria-label="GestãoPro — página inicial">
          <div class="sidebar-logo-icon" aria-hidden="true">G</div>
          <div>
            <div class="sidebar-logo-text" data-i18n="app.name">GestãoPro</div>
            <div class="sidebar-logo-sub">ERP</div>
          </div>
        </a>

        <nav class="sidebar-nav" aria-label="Menu principal">
          <div class="sidebar-section-title" data-i18n="nav.section_main"></div>
          ${mainLinks.map(_navItem).join('')}
          ${isAdmin ? `
            <div class="sidebar-section-title" data-i18n="nav.section_admin"></div>
            ${adminLinks.map(_navItem).join('')}
          ` : ''}
        </nav>
      </aside>

      <header class="header" id="app-header" role="banner">
        <div class="header-left">
          <button class="hamburger" id="hamburger-btn"
            aria-label="Abrir menu de navegação"
            aria-expanded="false"
            aria-controls="sidebar">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </button>
          <div>
            <h1 class="header-title" id="header-title">${title}</h1>
          </div>
        </div>
        <div class="header-right">
          <select class="lang-selector" id="lang-select" aria-label="Selecionar idioma" title="Idioma">
            <option value="pt-BR">🇧🇷 PT</option>
            <option value="en">🇺🇸 EN</option>
            <option value="es">🇪🇸 ES</option>
          </select>
          <div class="header-user" role="status" aria-live="polite">
            <div class="header-avatar" aria-hidden="true">${initials}</div>
            <span id="header-username">${user ? user.name : ''}</span>
            <span class="header-role-badge" id="header-role"></span>
          </div>
          <button class="btn btn-secondary btn-sm" id="btn-logout"
            data-i18n="auth.logout"
            aria-label="Sair do sistema">Sair</button>
        </div>
      </header>

      <main class="main" id="main-content" role="main" tabindex="-1">
        <!-- conteúdo injetado pela página -->
      </main>

      <footer class="app-footer" role="contentinfo">
        <span data-i18n="app.name">GestãoPro</span>
        &copy; <span id="footer-year"></span>
        &mdash;
        <span data-i18n="app.tagline">Sistema ERP Integrado</span>
      </footer>
    `;

    document.getElementById('footer-year').textContent = new Date().getFullYear();

    // Language selector — sync with saved pref and handle change
    const sel = document.getElementById('lang-select');
    if (sel) {
      const saved = localStorage.getItem('gestaopro_lang') || navigator.language || 'pt-BR';
      // Normalize navigator.language (e.g. 'pt' → 'pt-BR')
      const normalized = saved.startsWith('pt') ? 'pt-BR' : saved.startsWith('es') ? 'es' : 'en';
      sel.value = normalized;
      sel.addEventListener('change', () => I18N.load(sel.value));
    }

    // Update role badge
    if (user) {
      const badge = document.getElementById('header-role');
      if (badge) {
        badge.textContent = user.role;
        badge.className = `header-role-badge role-${user.role}`;
      }
    }

    // Logout
    document.getElementById('btn-logout')?.addEventListener('click', () => Auth.logout());

    // Close sidebar when any nav link is clicked (mobile)
    document.querySelectorAll('.sidebar-link').forEach(link =>
      link.addEventListener('click', _closeSidebar)
    );

    // Overlay click closes sidebar
    document.getElementById('sidebar-overlay')?.addEventListener('click', _closeSidebar);
  }

  function _setupHamburger() {
    const btn = document.getElementById('hamburger-btn');
    if (!btn) return;

    btn.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      const overlay = document.getElementById('sidebar-overlay');
      const open    = sidebar.classList.toggle('open');
      overlay.classList.toggle('open', open);
      btn.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    });

    // Close on Esc
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') _closeSidebar();
    });
  }

  function _closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const btn     = document.getElementById('hamburger-btn');
    if (sidebar) { sidebar.classList.remove('open'); }
    if (overlay) { overlay.classList.remove('open'); }
    if (btn)     { btn.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
  }

  function _markActive() {
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
      const href = link.getAttribute('href') || '';
      // Match if path ends with the page filename
      const hrefPage = href.split('/').pop();
      if (hrefPage && path.endsWith(hrefPage)) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      }
    });
    // Special case: root → dashboard
    if (path === '/' || path.endsWith('index.html')) {
      document.querySelector('[data-nav="dashboard"]')?.classList.add('active');
    }
  }

  return { init };
})();
