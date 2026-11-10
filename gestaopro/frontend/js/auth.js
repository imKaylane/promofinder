// =========================================================
// GestãoPro — Módulo de Autenticação (EX6)
// Portado de: backend/app/core/security.py (lógica JWT)
//             frontend/src/hooks/useAuth.tsx (fluxo)
//             frontend/src/services/api.ts (interceptors)
// Depende de: config.js (carregado antes)
// =========================================================

const Auth = (() => {
  const STORAGE_USER = 'gestaopro_user';

  // ── Storage helpers ────────────────────────────────────
  function getAccessToken()  { return localStorage.getItem('gestaopro_access'); }
  function getRefreshToken() { return localStorage.getItem('gestaopro_refresh'); }
  function isAuthenticated() { return !!getAccessToken(); }
  function getUser() {
    const s = sessionStorage.getItem(STORAGE_USER);
    return s ? JSON.parse(s) : null;
  }

  // ── Login ──────────────────────────────────────────────
  async function login(email, password) {
    const cfg = window.GestaoConfig;
    const url = cfg ? cfg.ENDPOINTS.LOGIN : '/api/v1/auth/login';

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw Object.assign(new Error(err.detail || 'login_failed'), { status: res.status, data: err });
    }
    const data = await res.json();
    localStorage.setItem('gestaopro_access', data.access_token);
    localStorage.setItem('gestaopro_refresh', data.refresh_token);

    // Busca o perfil do usuário após login
    const meUrl = cfg ? cfg.ENDPOINTS.ME : '/api/v1/auth/me';
    const me = await fetchWithAuth(meUrl);
    sessionStorage.setItem(STORAGE_USER, JSON.stringify(me));
    return me;
  }

  // ── Logout ─────────────────────────────────────────────
  async function logout() {
    const rt = getRefreshToken();
    if (rt) {
      try {
        const cfg = window.GestaoConfig;
        await fetchWithAuth(cfg ? cfg.ENDPOINTS.LOGOUT : '/api/v1/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: rt }),
        });
      } catch (_) {}
    }
    _clearStorage();
    window.location.href = '/';
  }

  function _clearStorage() {
    localStorage.removeItem('gestaopro_access');
    localStorage.removeItem('gestaopro_refresh');
    sessionStorage.removeItem(STORAGE_USER);
  }

  // ── Token refresh silencioso ───────────────────────────
  async function _refresh() {
    const rt = getRefreshToken();
    if (!rt) throw new Error('no_refresh');
    const cfg = window.GestaoConfig;
    const url = cfg ? cfg.ENDPOINTS.REFRESH : '/api/v1/auth/refresh';
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!res.ok) throw new Error('refresh_failed');
    const data = await res.json();
    localStorage.setItem('gestaopro_access', data.access_token);
    localStorage.setItem('gestaopro_refresh', data.refresh_token);
    return data.access_token;
  }

  // ── fetchWithAuth — Fetch autenticado + refresh automático ──
  async function fetchWithAuth(url, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    const token = getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let res = await fetch(url, { ...opts, headers });

    // Tenta renovar token em caso de 401
    if (res.status === 401) {
      try {
        const newToken = await _refresh();
        headers['Authorization'] = `Bearer ${newToken}`;
        res = await fetch(url, { ...opts, headers });
      } catch (_) {
        _clearStorage();
        window.location.href = '/';
        throw new Error('session_expired');
      }
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw Object.assign(new Error(err.detail || 'request_error'), { status: res.status, data: err });
    }
    if (res.status === 204) return null;
    return res.json();
  }

  // ── requireAuth — redireciona se não autenticado ───────
  function requireAuth() {
    if (!isAuthenticated()) {
      window.location.href = '/';
      return false;
    }
    return true;
  }

  return {
    login, logout, fetchWithAuth,
    getUser, getAccessToken, getRefreshToken,
    isAuthenticated, requireAuth,
  };
})();
